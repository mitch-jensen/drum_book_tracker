import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';
import { type Book, BookPage } from './playwright-book-page';

type Author = {
  firstName: string;
  lastName: string;
};

let bookSequence = 0;
const BOOK_AUTHOR_FIRST_NAME_PREFIX = 'E2EBookAuthorFirst';
const BOOK_TITLE_PREFIX = 'E2E Book';

function createAuthor(): Author {
  bookSequence += 1;

  return {
    firstName: `${BOOK_AUTHOR_FIRST_NAME_PREFIX}${bookSequence}`,
    lastName: `E2EBookAuthorLast${bookSequence}`,
  };
}

function createBook(author: Author): Book {
  bookSequence += 1;

  return {
    title: `${BOOK_TITLE_PREFIX} ${bookSequence}`,
    pageCount: `${100 + bookSequence}`,
    authorName: `${author.firstName} ${author.lastName}`,
  };
}

test.describe('Books page', () => {
  test.describe.configure({ mode: 'serial' });
  let authorPage: AuthorPage;
  let bookPage: BookPage;
  let author: Author;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    bookPage = new BookPage(page);
    author = createAuthor();

    await bookPage.goto();
    await bookPage.deleteAllBooks(BOOK_TITLE_PREFIX);

    await authorPage.goto();
    await authorPage.deleteAllAuthors(BOOK_AUTHOR_FIRST_NAME_PREFIX);
    await authorPage.addAuthor(author.firstName, author.lastName);

    await bookPage.goto();
  });

  test.afterEach(async () => {
    await bookPage.deleteAllBooks(BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(BOOK_AUTHOR_FIRST_NAME_PREFIX);
  });

  test.describe('adding a book', () => {
    test('adds a single book and shows it in the table', async () => {
      const book = createBook(author);

      await bookPage.addBook(book);

      await expect(bookPage.getRow(book)).toBeVisible();
    });

    test('adds multiple books and shows them in the table', async () => {
      const book = createBook(author);
      const secondBook = createBook(author);

      await bookPage.addBook(book);
      await bookPage.addBook(secondBook);

      await expect(bookPage.getRow(book)).toBeVisible();
      await expect(bookPage.getRow(secondBook)).toBeVisible();
    });

    test('clears the form after a successful submission', async () => {
      const book = createBook(author);

      await bookPage.addBook(book);

      await expect(bookPage.createTitleInput).toHaveValue('');
      await expect(bookPage.createPageCountInput).toHaveValue('');
    });
  });

  test.describe('add book form validation', () => {
    test('does not create a book if title is missing', async () => {
      const book = createBook(author);

      await bookPage.createPageCountInput.fill(book.pageCount);
      await bookPage.createAuthorsSelect.selectOption({ label: book.authorName });
      await bookPage.createSubmitButton.click();

      await expect(bookPage.getRowsByTitlePrefix(BOOK_TITLE_PREFIX)).toHaveCount(0);
    });

    test('does not create a book if page count is missing', async () => {
      const book = createBook(author);

      await bookPage.createTitleInput.fill(book.title);
      await bookPage.createAuthorsSelect.selectOption({ label: book.authorName });
      await bookPage.createSubmitButton.click();

      await expect(bookPage.getRowsByTitlePrefix(BOOK_TITLE_PREFIX)).toHaveCount(0);
    });
  });

  test.describe('editing a book', () => {
    test('shows inline inputs when Edit is clicked', async () => {
      const book = createBook(author);

      await bookPage.addBook(book);

      const row = await bookPage.openEdit(book);

      await expect(row.getByRole('textbox')).toBeVisible();
      await expect(row.getByRole('spinbutton')).toBeVisible();
      await expect(row.locator('select[name="authors"]')).toBeVisible();
      await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
      await expect(row.getByRole('button', { name: /cancel/i })).toBeVisible();
    });

    test('saves updated book details', async () => {
      const book = createBook(author);
      const updatedBook = createBook(author);

      await bookPage.addBook(book);
      await bookPage.editBook(book, updatedBook);

      await expect(bookPage.getRow(updatedBook)).toBeVisible();
      await expect(bookPage.getRow(book)).toHaveCount(0);
    });
  });

  test.describe('books table', () => {
    test('shows no test-created book on a fresh page', async () => {
      await expect(bookPage.getRowsByTitlePrefix(BOOK_TITLE_PREFIX)).toHaveCount(0);
    });

    test('shows the empty-state message after deleting the last book', async () => {
      const book = createBook(author);

      await bookPage.addBook(book);
      await bookPage.deleteBook(book);

      await expect(bookPage.getRow(book)).toHaveCount(0);
    });
  });
});
