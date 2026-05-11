import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';

type Author = {
  firstName: string;
  lastName: string;
};

let authorSequence = 0;

function createRandomUser(): Author {
  authorSequence += 1;

  return {
    firstName: `E2EFirst${authorSequence}`,
    lastName: `E2ELast${authorSequence}`,
  };
}

test.describe('Authors page', () => {
  test.describe.configure({ mode: 'serial' });
  let authorPage: AuthorPage;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    await authorPage.goto();
  });

  test.afterEach(async () => {
    await authorPage.deleteAllAuthors();
  });

  test.describe('adding an author', () => {
    test('adds a single author and shows them in the table', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      await expect(authorPage.getRow(author.firstName, author.lastName)).toBeVisible();
    });

    test('adds multiple authors and shows them in the table', async () => {
      const author1 = createRandomUser();
      const author2 = createRandomUser();

      await authorPage.addAuthor(author1.firstName, author1.lastName);
      await authorPage.addAuthor(author2.firstName, author2.lastName);

      await expect(authorPage.getRow(author1.firstName, author1.lastName)).toBeVisible();
      await expect(authorPage.getRow(author2.firstName, author2.lastName)).toBeVisible();
    });

    test('clears the form after a successful submission', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      await expect(authorPage.createFirstNameInput).toHaveValue('');
      await expect(authorPage.createLastNameInput).toHaveValue('');
    });
  });

  test.describe('add author form validation', () => {
    test('does not create author if first name missing', async () => {
      const author = createRandomUser();
      await authorPage.createLastNameInput.fill(author.lastName);
      await authorPage.createSubmitButton.click();

      await expect(authorPage.getAllRows()).toHaveCount(0);
      await expect(authorPage.getRow(author.firstName, author.lastName)).toHaveCount(0);
    });

    test('does not create author if last name missing', async () => {
      const author = createRandomUser();
      await authorPage.createFirstNameInput.fill(author.firstName);
      await authorPage.createSubmitButton.click();

      await expect(authorPage.getAllRows()).toHaveCount(0);
      await expect(authorPage.getRow(author.firstName, author.lastName)).toHaveCount(0);
    });

    test('does not create author if both fields missing', async () => {
      await authorPage.createSubmitButton.click();

      await expect(authorPage.getAllRows()).toHaveCount(0);
    });
  });

  test.describe('editing an author', () => {
    test('shows inline inputs when Edit is clicked', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      const row = await authorPage.openEdit(author.firstName, author.lastName);

      const inputs = row.getByRole('textbox');

      await expect(inputs.nth(0)).toBeVisible();
      await expect(inputs.nth(1)).toBeVisible();
      await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
      await expect(row.getByRole('button', { name: /cancel/i })).toBeVisible();
    });

    test('pre-fills inline inputs with existing values', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      const row = await authorPage.openEdit(author.firstName, author.lastName);

      const inputs = row.getByRole('textbox');

      await expect(inputs.nth(0)).toHaveValue(author.firstName);
      await expect(inputs.nth(1)).toHaveValue(author.lastName);
    });

    test('saves updated author details', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      const updatedAuthor = createRandomUser();

      await authorPage.editAuthor(
        author.firstName,
        author.lastName,
        updatedAuthor.firstName,
        updatedAuthor.lastName
      );

      await expect(
        authorPage.getRow(updatedAuthor.firstName, updatedAuthor.lastName)
      ).toBeVisible();

      await expect(
        authorPage.getRow(author.firstName, author.lastName)
      ).toHaveCount(0);
    });

    test('replaces inline inputs with text after saving', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      const updatedAuthor = createRandomUser();

      await authorPage.editAuthor(
        author.firstName,
        author.lastName,
        updatedAuthor.firstName,
        updatedAuthor.lastName
      );

      const updatedRow = authorPage.getRow(
        updatedAuthor.firstName,
        updatedAuthor.lastName
      );

      await expect(updatedRow.getByRole('textbox')).toHaveCount(0);
      await expect(updatedRow.getByRole('button', { name: /save/i })).toHaveCount(0);
      await expect(updatedRow.getByRole('button', { name: /^edit$/i })).toBeVisible();
      await expect(updatedRow.getByRole('button', { name: /^delete$/i })).toBeVisible();
    });
  });

  test.describe('authors table', () => {
    test('shows no test-created author on a fresh page', async () => {
      const authors = await authorPage.getAllAuthors();
      expect(authors).toHaveLength(0);
    });

    test('shows the empty-state message when there are no author rows', async () => {
      await expect(authorPage.tbody).toContainText(/no authors yet/i);
    });

    test('shows the empty-state message after deleting the last author', async () => {
      const author = createRandomUser();
      await authorPage.addAuthor(author.firstName, author.lastName);

      await authorPage.deleteAuthor(author.firstName, author.lastName);

      const authors = await authorPage.getAllAuthors();
      expect(authors).toHaveLength(0);
      await expect(authorPage.tbody).toContainText(/no authors yet/i);
    });

    test('displays authors in sorted table output', async () => {
      const author = createRandomUser();
      const secondAuthor = createRandomUser();

      await authorPage.addAuthor(author.firstName, author.lastName);
      await authorPage.addAuthor(secondAuthor.firstName, secondAuthor.lastName);

      const authors = await authorPage.getAllAuthors();

      expect(authors).toContainEqual(author);
      expect(authors).toContainEqual(secondAuthor);
    });
  });
});
