import { expect, type Locator, type Page } from '@playwright/test';

export type Section = {
    bookTitle: string;
    title: string;
    order: string;
};

export class SectionPage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');
        this.createForm = page.locator('#section-bulk-create-form');
    }

    async goto() {
        await this.page.goto('/sections/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    async gotoBulkCreate() {
        await this.page.goto('/sections/bulk-create/');
        await expect(this.createForm).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRowsByTitlePrefix(titlePrefix: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name: new RegExp(`^${titlePrefix}`),
            }),
        });
    }

    getRow(section: Section): Locator {
        return this.getAllRows()
            .filter({
                has: this.page.getByRole('cell', {
                    name: section.bookTitle,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: section.title,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: section.order,
                    exact: true,
                }),
            });
    }

    async addSection(section: Section) {
        await this.addSections([section]);
    }

    async addSections(sections: Section[]) {
        if (sections.length === 0) {
            throw new Error('At least one section is required');
        }

        await this.gotoBulkCreate();
        await this.createBookSelect.selectOption({ label: sections[0].bookTitle });

        for (const [index, section] of sections.entries()) {
            if (index > 0) {
                await this.addRowButton.click();
            }

            await this.createTitleInputs.nth(index).fill(section.title);
            await this.createOrderInputs.nth(index).fill(section.order);
        }

        await this.createSubmitButton.click();

        await expect(this.table).toBeVisible();
        for (const section of sections) {
            await expect(this.getRow(section).first()).toBeVisible();
        }
    }

    async deleteSection(section: Section) {
        const row = this.getRow(section).first();
        await expect(row).toBeVisible();

        const initialCount = await this.getAllRows().count();

        await row.getByRole('button', { name: /^delete$/i }).click();
        await this.confirmDeleteButton.click();

        await expect(this.getRow(section)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    async deleteAllSections(titlePrefix?: string) {
        await this.goto();

        const rows = titlePrefix === undefined ? this.getAllRows() : this.getRowsByTitlePrefix(titlePrefix);

        while ((await rows.count()) > 0) {
            const initialCount = await rows.count();
            const row = rows.first();

            await expect(row).toBeVisible();
            await row.getByRole('button', { name: /^delete$/i }).click();
            await this.confirmDeleteButton.click();
            await expect(rows).toHaveCount(initialCount - 1);
        }

        await expect(rows).toHaveCount(0);

        if (titlePrefix === undefined) {
            await expect(this.tbody).toContainText(/no sections yet/i);
        }
    }

    async openEdit(section: Section): Promise<Locator> {
        const displayRow = this.getRow(section).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Section row for ${section.title} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);
        await expect(editRow.getByRole('textbox')).toBeVisible();

        return editRow;
    }

    async editSection(currentSection: Section, updatedSection: Section) {
        const row = await this.openEdit(currentSection);

        await row.locator('select[name="book"]').selectOption({ label: updatedSection.bookTitle });
        await row.getByRole('textbox').fill(updatedSection.title);
        await row.getByRole('spinbutton').fill(updatedSection.order);
        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(updatedSection)).toHaveCount(1);
        await expect(this.getRow(updatedSection).first()).toBeVisible();
    }

    get createBookSelect() {
        return this.createForm.locator('select[name="book"]');
    }

    get createTitleInput() {
        return this.createTitleInputs.nth(0);
    }

    get createOrderInput() {
        return this.createOrderInputs.nth(0);
    }

    get createTitleInputs() {
        return this.createForm.locator('input[name="section_title"]');
    }

    get createOrderInputs() {
        return this.createForm.locator('input[name="section_order"]');
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /create sections/i });
    }

    get addRowButton() {
        return this.createForm.getByRole('button', { name: /add section/i });
    }

    get confirmDeleteButton() {
        return this.tbody.getByRole('button', { name: /confirm delete/i });
    }
}
