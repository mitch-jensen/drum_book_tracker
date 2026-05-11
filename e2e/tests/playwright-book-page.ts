import { expect, type Locator, type Page } from '@playwright/test';

export type Book = {
    title: string;
    pageCount: string;
    authorName: string;
};

export class BookPage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');
        this.createForm = page.locator('#book-create-form');
    }

    async goto() {
        await this.page.goto('/books/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRow(book: Book): Locator {
        return this.getAllRows()
            .filter({
                has: this.page.getByRole('cell', {
                    name: book.title,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: book.pageCount,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: book.authorName,
                    exact: true,
                }),
            });
    }

    async bookCount(): Promise<number> {
        return await this.getAllRows().count();
    }

    async addBook(book: Book) {
        await this.createTitleInput.fill(book.title);
        await this.createPageCountInput.fill(book.pageCount);
        await this.createAuthorsSelect.selectOption({ label: book.authorName });
        await this.createSubmitButton.click();

        await expect(this.getRow(book).first()).toBeVisible();
        await expect(this.createTitleInput).toHaveValue('');
        await expect(this.createPageCountInput).toHaveValue('');
    }

    async deleteBook(book: Book) {
        const row = this.getRow(book).first();
        await expect(row).toBeVisible();

        const initialCount = await this.bookCount();

        await row.getByRole('button', { name: /^delete$/i }).click();

        const confirmButton = this.tbody.getByRole('button', {
            name: /confirm delete/i,
        });

        await expect(confirmButton).toBeVisible();
        await confirmButton.click();

        await expect(this.getRow(book)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    async deleteAllBooks() {
        await this.goto();

        while ((await this.getAllRows().count()) > 0) {
            const initialCount = await this.bookCount();
            const row = this.getAllRows().first();

            await expect(row).toBeVisible();
            await row.getByRole('button', { name: /^delete$/i }).click();

            const confirmButton = this.tbody.getByRole('button', {
                name: /confirm delete/i,
            });

            await expect(confirmButton).toBeVisible();
            await confirmButton.click();

            await expect(this.getAllRows()).toHaveCount(initialCount - 1);
        }

        await expect(this.getAllRows()).toHaveCount(0);
        await expect(this.tbody).toContainText(/no books yet/i);
    }

    async openEdit(book: Book): Promise<Locator> {
        const displayRow = this.getRow(book).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Book row for ${book.title} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);

        await expect(editRow.getByRole('textbox')).toBeVisible();

        return editRow;
    }

    async editBook(currentBook: Book, updatedBook: Book) {
        const row = await this.openEdit(currentBook);

        await row.getByRole('textbox').fill(updatedBook.title);
        await row.getByRole('spinbutton').fill(updatedBook.pageCount);
        await row.locator('select[name="authors"]').selectOption({
            label: updatedBook.authorName,
        });
        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(updatedBook)).toHaveCount(1);
        await expect(this.getRow(updatedBook).first()).toBeVisible();
    }

    async getAllBooks(): Promise<Book[]> {
        const rows = await this.getAllRows().all();
        const result: Book[] = [];

        for (const row of rows) {
            const cells = row.getByRole('cell');

            result.push({
                title: (await cells.nth(0).textContent())?.trim() ?? '',
                pageCount: (await cells.nth(1).textContent())?.trim() ?? '',
                authorName: (await cells.nth(2).textContent())?.trim() ?? '',
            });
        }

        return result;
    }

    get createTitleInput() {
        return this.createForm.getByRole('textbox').nth(0);
    }

    get createPageCountInput() {
        return this.createForm.getByRole('spinbutton').nth(0);
    }

    get createAuthorsSelect() {
        return this.createForm.locator('select[name="authors"]');
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /add/i });
    }
}
