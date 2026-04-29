import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';

test.describe('Authors page', () => {
  let authorPage: AuthorPage;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    await authorPage.goto();
  });

  // ─── Add Author ───────────────────────────────────────────────────────────

  test.describe('adding an author', () => {
    test.afterEach(async () => {
      await authorPage.deleteAllAuthors();
    });

    test('adds a single author and shows them in the table', async () => {
      await authorPage.addAuthor('Gary', 'Chaffee');
      await expect(authorPage.getRowByAuthor('Gary', 'Chaffee')).resolves.toBeVisible();
    });

    test('increments the author count after adding', async () => {
      const initialCount = await authorPage.getNumberOfAuthors();
      await authorPage.addAuthor('Gary', 'Chaffee');
      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(initialCount + 1);
    });

    test('clears the form after a successful submission', async () => {
      await authorPage.addAuthor('Gary', 'Chaffee');
      await expect(authorPage.addAuthorFirstName).toHaveValue('');
      await expect(authorPage.addAuthorLastName).toHaveValue('');
    });

    test('Add Author button is disabled while submitting', async ({ page }) => {
      // Slow the HTMX response down so we can catch the disabled state
      await page.route('**/authors/create/**', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 500));
        await route.continue();
      });

      await authorPage.addAuthorFirstName.fill('Gary');
      await authorPage.addAuthorLastName.fill('Chaffee');
      await authorPage.addAuthorButton.click();

      await expect(authorPage.addAuthorButton).toBeDisabled();
    });
  });

  // ─── Form Validation ──────────────────────────────────────────────────────

  test.describe('add author form validation', () => {
    test('requires first name', async () => {
      await authorPage.addAuthorLastName.fill('Chaffee');
      await authorPage.addAuthorButton.click();

      await expect(authorPage.addAuthorFirstName).toBeFocused();
      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(0);
    });

    test('requires last name', async () => {
      await authorPage.addAuthorFirstName.fill('Gary');
      await authorPage.addAuthorButton.click();

      await expect(authorPage.addAuthorLastName).toBeFocused();
      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(0);
    });

    test('requires both fields to be filled before submission', async () => {
      await authorPage.addAuthorButton.click();

      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(0);
    });
  });

  // ─── Edit Author ──────────────────────────────────────────────────────────

  test.describe('editing an author', () => {
    test.beforeEach(async () => {
      await authorPage.addAuthor('Gary', 'Chaffee');
    });

    test.afterEach(async () => {
      await authorPage.deleteAllAuthors();
    });

    test('shows inline inputs when Edit is clicked', async () => {
      const row = await authorPage.openEditMode('Gary', 'Chaffee');

      await expect(row.getByRole('textbox').nth(0)).toBeVisible();
      await expect(row.getByRole('textbox').nth(1)).toBeVisible();
      await expect(row.getByRole('button', { name: 'Save' })).toBeVisible();
    });

    test('pre-fills inline inputs with existing values', async () => {
      const row = await authorPage.openEditMode('Gary', 'Chaffee');

      await expect(row.getByRole('textbox').nth(0)).toHaveValue('Gary');
      await expect(row.getByRole('textbox').nth(1)).toHaveValue('Chaffee');
    });

    test('saves updated author details', async () => {
      await authorPage.editAuthor('Gary', 'Chaffee', 'Gary', 'Chester');

      await expect(authorPage.getRowByAuthor('Gary', 'Chester')).resolves.toBeVisible();
      await expect(authorPage.getRowByAuthor('Gary', 'Chaffee')).resolves.not.toBeVisible();
    });

    test('does not change the author count after editing', async () => {
      const countBefore = await authorPage.getNumberOfAuthors();

      await authorPage.editAuthor('Gary', 'Chaffee', 'Gary', 'Chester');

      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(countBefore);
    });

    test('replaces inline inputs with text after saving', async () => {
      const row = await authorPage.openEditMode('Gary', 'Chaffee');
      await authorPage.editAuthor('Gary', 'Chaffee', 'Gary', 'Chester');

      await expect(row.getByRole('textbox')).resolves.not.toBeVisible();
      await expect(row.getByRole('button', { name: 'Save' })).resolves.not.toBeVisible();
      await expect(row.getByRole('button', { name: 'Edit' })).resolves.toBeVisible();
    });
  });

  // ─── Table State ──────────────────────────────────────────────────────────

  test.describe('authors table', () => {
    test('shows an empty table on a fresh page', async () => {
      await expect(authorPage.getNumberOfAuthors()).resolves.toBe(0);
    });

    test('displays authors in the order they were added', async () => {
      await authorPage.addAuthor('Gary', 'Chaffee');
      await authorPage.addAuthor('Joe', 'Morello');

      const authors = await authorPage.getAllAuthors();
      expect(authors[0]).toEqual({ firstName: 'Gary', lastName: 'Chaffee' });
      expect(authors[1]).toEqual({ firstName: 'Joe', lastName: 'Morello' });

      await authorPage.deleteAuthorIfExists('Gary', 'Chaffee');
      await authorPage.deleteAuthorIfExists('Joe', 'Morello');
    });
  });
});
