import { expect, type Locator, type Page } from '@playwright/test';

export type Section = {
    bookTitle: string;
    title: string;
};

export class SectionPage {
    readonly page: Page;

    readonly listContainer: Locator;
    readonly sectionBody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.listContainer = page.locator('#section-list-container');
        this.sectionBody = page.locator('#section-table-body');
        this.createForm = page.locator('#section-bulk-create-form');
    }

    async goto() {
        await this.page.goto('/sections/');
        await expect(this.listContainer).toBeVisible();
        await expect(this.sectionBody).toBeVisible();
    }

    async gotoBulkCreate() {
        await this.page.goto('/sections/bulk-create/');
        await expect(this.createForm).toBeVisible();
    }

    getAllRows(): Locator {
        return this.sectionBody.locator('.list-group-item').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRowsByTitlePrefix(titlePrefix: string): Locator {
        return this.getAllRows().filter({
            hasText: new RegExp(titlePrefix),
        });
    }

    getRow(section: Section): Locator {
        return this.page
            .locator('section')
            .filter({
                has: this.page.getByRole('heading', {
                    name: section.bookTitle,
                    exact: true,
                }),
            })
            .locator('.list-group-item')
            .filter({
                has: this.page.getByRole('button', { name: /^delete$/i }),
            })
            .filter({
                hasText: new RegExp(`^\\s*${section.title}\\s*Edit\\s*Delete\\s*$`),
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
        }

        await this.createSubmitButton.click();

        await expect(this.listContainer).toBeVisible();
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
            await expect(this.sectionBody).toContainText(/no sections yet/i);
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

        const editRow = this.sectionBody.locator(`[id="${rowId}"]`);
        await expect(editRow.getByRole('textbox')).toBeVisible();

        return editRow;
    }

    async editSection(currentSection: Section, updatedSection: Section) {
        const row = await this.openEdit(currentSection);

        await row.getByRole('textbox').fill(updatedSection.title);
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

    get createTitleInputs() {
        return this.createForm.locator('input[name="section_title"]');
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /create sections/i });
    }

    get addRowButton() {
        return this.createForm.getByRole('button', { name: /add section/i });
    }

    get confirmDeleteButton() {
        return this.sectionBody.getByRole('button', { name: /confirm delete/i });
    }
}
