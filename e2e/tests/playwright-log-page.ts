import { expect, type Locator, type Page } from '@playwright/test';

export type LogEntry = {
    bookTitle: string;
    sectionTitle: string;
    sectionName: string;
    exerciseName: string;
    pageNumber: string;
    practicedOn: string;
    tempo: string;
    notes: string;
};

export class LogPage {
    readonly page: Page;

    readonly table: Locator;
    readonly tbody: Locator;
    readonly createForm: Locator;

    constructor(page: Page) {
        this.page = page;
        this.table = page.getByRole('table');
        this.tbody = this.table.locator('tbody');
        this.createForm = page.locator('#log-create-form');
    }

    async goto() {
        await this.page.goto('/logs/');
        await expect(this.table).toBeVisible();
        await expect(this.tbody).toBeVisible();
    }

    getAllRows(): Locator {
        return this.tbody.getByRole('row').filter({
            has: this.page.getByRole('button', { name: /^delete$/i }),
        });
    }

    getRowsByNotesPrefix(notesPrefix: string): Locator {
        return this.getAllRows().filter({
            has: this.page.getByRole('cell', {
                name: new RegExp(`^${notesPrefix}`),
            }),
        });
    }

    getRow(logEntry: LogEntry): Locator {
        return this.getAllRows()
            .filter({
                has: this.page.getByRole('cell', {
                    name: logEntry.bookTitle,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: logEntry.sectionTitle,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: logEntry.pageNumber,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: logEntry.exerciseName,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: `${logEntry.tempo} BPM`,
                    exact: true,
                }),
            })
            .filter({
                has: this.page.getByRole('cell', {
                    name: logEntry.notes,
                    exact: true,
                }),
            });
    }

    async addLog(logEntry: LogEntry) {
        await this.createBookSelect.selectOption({ label: logEntry.bookTitle });
        await expect(this.createSectionSelect.locator('option', { hasText: logEntry.sectionName })).toHaveCount(1);
        await this.createSectionSelect.selectOption({ label: logEntry.sectionName });
        await expect(this.createExerciseSelect.locator('option', { hasText: logEntry.exerciseName })).toHaveCount(1);
        await this.createExerciseSelect.selectOption({ label: logEntry.exerciseName });
        await this.createDateInput.fill(logEntry.practicedOn);
        await this.createTempoInput.fill(logEntry.tempo);
        await this.createNotesInput.fill(logEntry.notes);
        await this.createSubmitButton.click();

        await expect(this.getRow(logEntry).first()).toBeVisible();
        await expect(this.createTempoInput).toHaveValue('');
        await expect(this.createNotesInput).toHaveValue('');
    }

    async deleteLog(logEntry: LogEntry) {
        const row = this.getRow(logEntry).first();
        await expect(row).toBeVisible();

        const initialCount = await this.getAllRows().count();

        await row.getByRole('button', { name: /^delete$/i }).click();
        await this.confirmDeleteButton.click();

        await expect(this.getRow(logEntry)).toHaveCount(0);
        await expect(this.getAllRows()).toHaveCount(initialCount - 1);
    }

    async deleteAllLogs(notesPrefix?: string) {
        await this.goto();

        const rows = notesPrefix === undefined ? this.getAllRows() : this.getRowsByNotesPrefix(notesPrefix);

        while ((await rows.count()) > 0) {
            const initialCount = await rows.count();
            const row = rows.first();

            await expect(row).toBeVisible();
            await row.getByRole('button', { name: /^delete$/i }).click();
            await this.confirmDeleteButton.click();
            await expect(rows).toHaveCount(initialCount - 1);
        }

        await expect(rows).toHaveCount(0);

        if (notesPrefix === undefined) {
            await expect(this.tbody).toContainText(/no log entries yet/i);
        }
    }

    async openEdit(logEntry: LogEntry): Promise<Locator> {
        const displayRow = this.getRow(logEntry).first();
        await expect(displayRow).toBeVisible();

        const rowId = await displayRow.getAttribute('id');

        if (rowId === null) {
            throw new Error(`Log row for ${logEntry.exerciseName} does not have an id`);
        }

        await displayRow.getByRole('button', { name: /^edit$/i }).click();

        const editRow = this.tbody.locator(`tr[id="${rowId}"]`);
        await expect(editRow.locator('select[name="exercise"]')).toBeVisible();

        return editRow;
    }

    async editLog(currentLogEntry: LogEntry, updatedLogEntry: LogEntry) {
        const row = await this.openEdit(currentLogEntry);

        await row.locator('select[name="book"]').selectOption({ label: updatedLogEntry.bookTitle });
        await expect(row.locator('select[name="section"] option', { hasText: updatedLogEntry.sectionName })).toHaveCount(1);
        await row.locator('select[name="section"]').selectOption({ label: updatedLogEntry.sectionName });
        await expect(row.locator('select[name="exercise"] option', { hasText: updatedLogEntry.exerciseName })).toHaveCount(1);
        await row.locator('select[name="exercise"]').selectOption({ label: updatedLogEntry.exerciseName });
        await row.locator('input[name="practiced_on"]').fill(updatedLogEntry.practicedOn);
        await row.locator('input[name="tempo"]').fill(updatedLogEntry.tempo);
        await row.locator('textarea[name="notes"]').fill(updatedLogEntry.notes);
        await row.getByRole('button', { name: /^save$/i }).click();

        await expect(this.getRow(updatedLogEntry)).toHaveCount(1);
        await expect(this.getRow(updatedLogEntry).first()).toBeVisible();
    }

    get createBookSelect() {
        return this.createForm.locator('select[name="book"]');
    }

    get createSectionSelect() {
        return this.createForm.locator('select[name="section"]');
    }

    get createExerciseSelect() {
        return this.createForm.locator('select[name="exercise"]');
    }

    get createDateInput() {
        return this.createForm.locator('input[name="practiced_on"]');
    }

    get createTempoInput() {
        return this.createForm.locator('input[name="tempo"]');
    }

    get createNotesInput() {
        return this.createForm.locator('textarea[name="notes"]');
    }

    get createSubmitButton() {
        return this.createForm.getByRole('button', { name: /add/i });
    }

    get confirmDeleteButton() {
        return this.tbody.getByRole('button', { name: /confirm delete/i });
    }
}
