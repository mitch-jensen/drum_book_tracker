import { expect, type Locator, type Page } from '@playwright/test';

export class TagPage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');
        this.createForm = page.locator('#tag-create-form');
    }

    async goto() {
        await this.page.goto('/tags/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRow(name: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name,
                exact: true,
            }),
        });
    }

    async tagCount(): Promise<number> {
        return await this.getAllRows().count();
    }

    async addTag(name: string) {
        await this.createNameInput.fill(name);
        await this.createSubmitButton.click();

        await expect(this.getRow(name).first()).toBeVisible();
        await expect(this.createNameInput).toHaveValue('');
    }

    async deleteTag(name: string) {
        const row = this.getRow(name).first();
        await expect(row).toBeVisible();

        const initialCount = await this.tagCount();

        await row.getByRole('button', { name: /^delete$/i }).click();

        const confirmButton = this.tbody.getByRole('button', {
            name: /confirm delete/i,
        });

        await expect(confirmButton).toBeVisible();
        await confirmButton.click();

        await expect(this.getRow(name)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    getRowsByNamePrefix(namePrefix: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name: new RegExp(`^${namePrefix}`),
            }),
        });
    }

    async deleteAllTags(namePrefix?: string) {
        await this.goto();

        const rows = namePrefix === undefined ? this.getAllRows() : this.getRowsByNamePrefix(namePrefix);

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

        if (namePrefix === undefined) {
            await expect(this.tbody).toContainText(/no tags yet/i);
        }
    }

    async openEdit(name: string): Promise<Locator> {
        const displayRow = this.getRow(name).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Tag row for ${name} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);
        const input = editRow.getByRole('textbox');

        await expect(input).toBeVisible();

        return editRow;
    }

    async editTag(currentName: string, newName: string) {
        const row = await this.openEdit(currentName);

        await row.getByRole('textbox').fill(newName);
        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(newName)).toHaveCount(1);
        await expect(this.getRow(newName).first()).toBeVisible();
    }

    async getAllTags(): Promise<string[]> {
        const rows = await this.getAllRows().all();
        const result: string[] = [];

        for (const row of rows) {
            result.push((await row.getByRole('cell').first().textContent())?.trim() ?? '');
        }

        return result;
    }

    get createNameInput() {
        return this.createForm.getByRole('textbox').nth(0);
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /add/i });
    }
}
