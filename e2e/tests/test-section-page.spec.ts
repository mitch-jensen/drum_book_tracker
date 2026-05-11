import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';
import { type Book, BookPage } from './playwright-book-page';
import { type Section, SectionPage } from './playwright-section-page';

let sectionSequence = 0;
const SECTION_AUTHOR_FIRST_NAME_PREFIX = 'E2ESectionAuthorFirst';
const SECTION_BOOK_TITLE_PREFIX = 'E2E Section Book';
const SECTION_TITLE_PREFIX = 'E2E Section';

function createAuthor() {
  sectionSequence += 1;

  return {
    firstName: `${SECTION_AUTHOR_FIRST_NAME_PREFIX}${sectionSequence}`,
    lastName: `E2ESectionAuthorLast${sectionSequence}`,
  };
}

function createBook(authorName: string): Book {
  sectionSequence += 1;

  return {
    title: `${SECTION_BOOK_TITLE_PREFIX} ${sectionSequence}`,
    pageCount: `${120 + sectionSequence}`,
    authorName,
  };
}

function createSection(bookTitle: string): Section {
  sectionSequence += 1;

  return {
    bookTitle,
    title: `${SECTION_TITLE_PREFIX} ${sectionSequence}`,
  };
}

test.describe('Sections page', () => {
  test.describe.configure({ mode: 'serial' });
  let authorPage: AuthorPage;
  let bookPage: BookPage;
  let sectionPage: SectionPage;
  let book: Book;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    bookPage = new BookPage(page);
    sectionPage = new SectionPage(page);

    await sectionPage.deleteAllSections(SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(SECTION_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(SECTION_AUTHOR_FIRST_NAME_PREFIX);

    const author = createAuthor();
    await authorPage.addAuthor(author.firstName, author.lastName);

    book = createBook(`${author.firstName} ${author.lastName}`);
    await bookPage.goto();
    await bookPage.addBook(book);

    await sectionPage.goto();
  });

  test.afterEach(async () => {
    await sectionPage.deleteAllSections(SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(SECTION_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(SECTION_AUTHOR_FIRST_NAME_PREFIX);
  });

  test('adds a section and shows it in the list', async () => {
    const section = createSection(book.title);

    await sectionPage.addSection(section);

    await expect(sectionPage.getRow(section)).toBeVisible();
  });

  test('adds multiple sections for one book and shows them in the list', async () => {
    const section = createSection(book.title);
    const secondSection = createSection(book.title);

    await sectionPage.addSections([section, secondSection]);

    await expect(sectionPage.getRow(section)).toBeVisible();
    await expect(sectionPage.getRow(secondSection)).toBeVisible();
  });

  test('does not create a section if title is missing', async () => {
    const section = createSection(book.title);

    await sectionPage.gotoBulkCreate();
    await sectionPage.createBookSelect.selectOption({ label: section.bookTitle });
    await sectionPage.createSubmitButton.click();

    await expect(sectionPage.createForm).toBeVisible();
    await sectionPage.goto();
    await expect(sectionPage.getRowsByTitlePrefix(SECTION_TITLE_PREFIX)).toHaveCount(0);
  });

  test('shows inline inputs when Edit is clicked', async () => {
    const section = createSection(book.title);

    await sectionPage.addSection(section);

    const row = await sectionPage.openEdit(section);

    await expect(row.getByRole('textbox')).toBeVisible();
    await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
  });

  test('saves updated section details', async () => {
    const section = createSection(book.title);
    const updatedSection = createSection(book.title);

    await sectionPage.addSection(section);
    await sectionPage.editSection(section, updatedSection);

    await expect(sectionPage.getRow(updatedSection)).toBeVisible();
    await expect(sectionPage.getRow(section)).toHaveCount(0);
  });

  test('removes a deleted test-created section from the list', async () => {
    const section = createSection(book.title);

    await sectionPage.addSection(section);
    await sectionPage.deleteSection(section);

    await expect(sectionPage.getRow(section)).toHaveCount(0);
  });
});
