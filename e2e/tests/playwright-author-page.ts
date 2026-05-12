import { expect, type Locator, type Page } from '@playwright/test';

export class AuthorPage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;

        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');

        // Match your updated template id.
        this.createForm = page.locator('#author-create-form');
    }

    async goto() {
        await this.page.goto('/authors/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRow(firstName: string, lastName: string): Locator {
        return this.getAllRows()
            .filter({
                has: this.page.getByRole('cell', {
                    name: firstName,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: lastName,
                    exact: true,
                }),
            });
    }

    async rowExists(firstName: string, lastName: string): Promise<boolean> {
        return await this.getRow(firstName, lastName).first().isVisible();
    }

    async rowCount(): Promise<number> {
        return await this.authorCount();
    }

    async authorCount(): Promise<number> {
        return await this.getAllRows().count();
    }

    async addAuthor(firstName: string, lastName: string) {
        await this.createFirstNameInput.fill(firstName);
        await this.createLastNameInput.fill(lastName);
        await this.createSubmitButton.click();

        await expect(this.getRow(firstName, lastName).first()).toBeVisible();

        // Verify form is cleared after submission
        await expect(this.createFirstNameInput).toHaveValue('');
        await expect(this.createLastNameInput).toHaveValue('');
    }

    async deleteAuthor(firstName: string, lastName: string) {
        const row = this.getRow(firstName, lastName).first();
        await expect(row).toBeVisible();

        const initialCount = await this.authorCount();

        await row.getByRole('button', { name: /^delete$/i }).click();

        const confirmButton = this.tbody.getByRole('button', {
            name: /confirm delete/i,
        });

        await expect(confirmButton).toBeVisible();
        await confirmButton.click();

        await expect(this.getRow(firstName, lastName)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    async deleteIfExists(firstName: string, lastName: string) {
        while ((await this.getRow(firstName, lastName).count()) > 0) {
            await this.deleteAuthor(firstName, lastName);
        }
    }

    getRowsByFirstNamePrefix(firstNamePrefix: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name: new RegExp(`^${firstNamePrefix}`),
            }),
        });
    }

    async deleteAllAuthors(firstNamePrefix?: string) {
        await this.goto();

        const rows = firstNamePrefix === undefined
            ? this.getAllRows()
            : this.getRowsByFirstNamePrefix(firstNamePrefix);

        while ((await rows.count()) > 0) {
            const initialCount = await rows.count();
            const row = rows.first();

            await expect(row).toBeVisible();
            await row.getByRole('button', { name: /^delete$/i }).click();

            const confirmButton = this.tbody.getByRole('button', {
                name: /confirm delete/i,
            });

            await expect(confirmButton).toBeVisible();
            await confirmButton.click();

            await expect(rows).toHaveCount(initialCount - 1);
        }

        await expect(rows).toHaveCount(0);

        if (firstNamePrefix === undefined) {
            await expect(this.tbody).toContainText(/no authors yet/i);
        }
    }

    async openEdit(firstName: string, lastName: string): Promise<Locator> {
        const displayRow = this.getRow(firstName, lastName).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Author row for ${firstName} ${lastName} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);
        const inputs = editRow.getByRole('textbox');

        await expect(inputs.first()).toBeVisible();

        return editRow;
    }

    async editAuthor(
        currentFirstName: string,
        currentLastName: string,
        newFirstName: string,
        newLastName: string
    ) {
        const row = await this.openEdit(currentFirstName, currentLastName);

        const inputs = row.getByRole('textbox');

        await inputs.nth(0).fill(newFirstName);
        await inputs.nth(1).fill(newLastName);

        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(newFirstName, newLastName)).toHaveCount(1);
        await expect(this.getRow(newFirstName, newLastName).first()).toBeVisible();
    }

    async getAllAuthors(): Promise<{ firstName: string; lastName: string }[]> {
        const rows = await this.getAllRows().all();

        const result: { firstName: string; lastName: string }[] = [];

        for (const row of rows) {
            const cells = row.getByRole('cell');

            result.push({
                firstName: (await cells.nth(0).textContent())?.trim() ?? '',
                lastName: (await cells.nth(1).textContent())?.trim() ?? '',
            });
        }

        return result;
    }

    get createFirstNameInput() {
        return this.createForm.getByRole('textbox').nth(0);
    }

    get createLastNameInput() {
        return this.createForm.getByRole('textbox').nth(1);
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /add/i });
    }
}
