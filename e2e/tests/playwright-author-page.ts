import { expect, type Locator, type Page } from '@playwright/test';

export class AuthorPage {
    readonly page: Page;

    // Add author form locators
    readonly addAuthorFirstName: Locator;
    readonly addAuthorLastName: Locator;
    readonly addAuthorButton: Locator;

    // Authors table
    readonly authorsTable: Locator;

    constructor(page: Page) {
        this.page = page;
        this.addAuthorFirstName = page.getByRole('textbox', { name: 'First name*' });
        this.addAuthorLastName = page.getByRole('textbox', { name: 'Last name*' });
        this.addAuthorButton = page.getByRole('button', { name: 'Add Author' })
        this.authorsTable = page.getByRole('table');
    }

    async getRowByAuthor(firstName: string, lastName: string): Promise<Locator> {
        return this.authorsTable
            .getByRole('row')
            .filter({ hasText: firstName })
            .filter({ hasText: lastName });
    }

    async getNumberOfAuthors(): Promise<number> {
        return this.authorsTable
            .getByRole('rowgroup')
            .last() // first rowgroup is <thead>, second is <tbody>
            .getByRole('row')
            .count();
    }

    async goto() {
        await this.page.goto('authors/');
    }

    async addAuthor(firstName: string, lastName: string) {
        await this.addAuthorFirstName.click();
        await this.addAuthorFirstName.fill(firstName);
        await this.addAuthorLastName.click();
        await this.addAuthorLastName.fill(lastName);
        await this.addAuthorButton.click();

        // Verify the new author appears in the table
        await expect(this.getRowByAuthor(firstName, lastName)).resolves.toBeVisible();
    }

    async deleteAuthorIfExists(firstName: string, lastName: string): Promise<void> {
        const row = await this.getRowByAuthor(firstName, lastName);
        if (await row.isVisible()) {
            await row.getByRole('button', { name: 'Delete' }).click();
        }
    }

    async getAllAuthors(): Promise<{ firstName: string; lastName: string }[]> {
        const rows = await this.authorsTable
            .getByRole('rowgroup')
            .last()
            .getByRole('row')
            .all();

        return Promise.all(
            rows.map(async (row) => {
                const cells = row.getByRole('cell');
                return {
                    firstName: (await cells.nth(0).innerText()).trim(),
                    lastName: (await cells.nth(1).innerText()).trim(),
                };
            })
        );
    }

    async deleteAllAuthors(): Promise<void> {
        const authors = await this.getAllAuthors();
        await Promise.all(
            authors.map(async (author) => {
                await this.deleteAuthorIfExists(author.firstName, author.lastName);
            })
        );
    }

    async openEditMode(firstName: string, lastName: string): Promise<Locator> {
        const row = await this.getRowByAuthor(firstName, lastName);
        await row.getByRole('button', { name: 'Edit' }).click();
        // Wait for the inline inputs to appear before returning
        await expect(row.getByRole('textbox').nth(0)).toBeVisible();
        return row;
    }

    async editAuthor(
        currentFirstName: string,
        currentLastName: string,
        newFirstName: string,
        newLastName: string
    ) {
        const row = await this.openEditMode(currentFirstName, currentLastName);

        const inputs = row.getByRole('textbox');
        await inputs.nth(0).clear();
        await inputs.nth(0).fill(newFirstName);
        await inputs.nth(1).clear();
        await inputs.nth(1).fill(newLastName);

        await row.getByRole('button', { name: 'Save' }).click();

        await expect(this.getRowByAuthor(newFirstName, newLastName)).resolves.toBeVisible();
    }
}
