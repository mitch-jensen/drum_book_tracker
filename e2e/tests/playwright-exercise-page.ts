import { expect, type Locator, type Page } from '@playwright/test';

export type Exercise = {
    sectionName: string;
    identifier: string;
    description: string;
    pageNumber: string;
    tagName: string;
};

export class ExercisePage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');
        this.createForm = page.locator('#exercise-create-form');
    }

    async goto() {
        await this.page.goto('/exercises/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRowsByIdentifierPrefix(identifierPrefix: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name: new RegExp(`^${identifierPrefix}`),
            }),
        });
    }

    getRow(exercise: Exercise): Locator {
        return this.getAllRows()
            .filter({
                has: this.page.getByRole('cell', {
                    name: exercise.sectionName,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: exercise.identifier,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: exercise.description,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: exercise.pageNumber,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: exercise.tagName,
                    exact: true,
                }),
            });
    }

    async addExercise(exercise: Exercise) {
        await this.createSectionSelect.selectOption({ label: exercise.sectionName });
        await this.createIdentifierInput.fill(exercise.identifier);
        await this.createDescriptionInput.fill(exercise.description);
        await this.createPageNumberInput.fill(exercise.pageNumber);
        await this.createTagsSelect.selectOption({ label: exercise.tagName });
        await this.createSubmitButton.click();

        await expect(this.getRow(exercise).first()).toBeVisible();
        await expect(this.createIdentifierInput).toHaveValue('');
        await expect(this.createDescriptionInput).toHaveValue('');
    }

    async deleteExercise(exercise: Exercise) {
        const row = this.getRow(exercise).first();
        await expect(row).toBeVisible();

        const initialCount = await this.getAllRows().count();

        await row.getByRole('button', { name: /^delete$/i }).click();
        await this.confirmDeleteButton.click();

        await expect(this.getRow(exercise)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    async deleteAllExercises(identifierPrefix?: string) {
        await this.goto();

        const rows = identifierPrefix === undefined ? this.getAllRows() : this.getRowsByIdentifierPrefix(identifierPrefix);

        while ((await rows.count()) > 0) {
            const initialCount = await rows.count();
            const row = rows.first();

            await expect(row).toBeVisible();
            await row.getByRole('button', { name: /^delete$/i }).click();
            await this.confirmDeleteButton.click();
            await expect(rows).toHaveCount(initialCount - 1);
        }

        await expect(rows).toHaveCount(0);

        if (identifierPrefix === undefined) {
            await expect(this.tbody).toContainText(/no exercises yet/i);
        }
    }

    async openEdit(exercise: Exercise): Promise<Locator> {
        const displayRow = this.getRow(exercise).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Exercise row for ${exercise.identifier} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);
        await expect(editRow.getByRole('textbox').first()).toBeVisible();

        return editRow;
    }

    async editExercise(currentExercise: Exercise, updatedExercise: Exercise) {
        const row = await this.openEdit(currentExercise);
        const textboxes = row.getByRole('textbox');

        await row.locator('select[name="section"]').selectOption({ label: updatedExercise.sectionName });
        await textboxes.nth(0).fill(updatedExercise.identifier);
        await textboxes.nth(1).fill(updatedExercise.description);
        await row.getByRole('spinbutton').fill(updatedExercise.pageNumber);
        await row.locator('select[name="tags"]').selectOption({ label: updatedExercise.tagName });
        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(updatedExercise)).toHaveCount(1);
        await expect(this.getRow(updatedExercise).first()).toBeVisible();
    }

    get createSectionSelect() {
        return this.createForm.locator('select[name="section"]');
    }

    get createIdentifierInput() {
        return this.createForm.getByRole('textbox').nth(0);
    }

    get createDescriptionInput() {
        return this.createForm.getByRole('textbox').nth(1);
    }

    get createPageNumberInput() {
        return this.createForm.getByRole('spinbutton').nth(0);
    }

    get createTagsSelect() {
        return this.createForm.locator('select[name="tags"]');
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /add/i });
    }

    get confirmDeleteButton() {
        return this.tbody.getByRole('button', { name: /confirm delete/i });
    }
}
