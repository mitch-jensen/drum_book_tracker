import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';
import { type Book, BookPage } from './playwright-book-page';
import { type Exercise, ExercisePage } from './playwright-exercise-page';
import { type LogEntry, LogPage } from './playwright-log-page';
import { type Section, SectionPage } from './playwright-section-page';
import { TagPage } from './playwright-tag-page';

let logSequence = 0;
const LOG_AUTHOR_FIRST_NAME_PREFIX = 'E2ELogAuthorFirst';
const LOG_BOOK_TITLE_PREFIX = 'E2E Log Book';
const LOG_SECTION_TITLE_PREFIX = 'E2E Log Section';
const LOG_EXERCISE_IDENTIFIER_PREFIX = 'E2ELogEx';
const LOG_TAG_NAME_PREFIX = 'E2ELogTag';
const LOG_NOTES_PREFIX = 'E2ELogNote';

function createAuthor() {
  logSequence += 1;

  return {
    firstName: `${LOG_AUTHOR_FIRST_NAME_PREFIX}${logSequence}`,
    lastName: `E2ELogAuthorLast${logSequence}`,
  };
}

function createBook(authorName: string): Book {
  logSequence += 1;

  return {
    title: `${LOG_BOOK_TITLE_PREFIX} ${logSequence}`,
    pageCount: `${160 + logSequence}`,
    authorName,
  };
}

function createSection(bookTitle: string): Section {
  logSequence += 1;

  return {
    bookTitle,
    title: `${LOG_SECTION_TITLE_PREFIX} ${logSequence}`,
    order: `${logSequence}`,
  };
}

function createExercise(sectionName: string, tagName: string): Exercise {
  logSequence += 1;

  return {
    sectionName,
    identifier: `${LOG_EXERCISE_IDENTIFIER_PREFIX}${logSequence}`,
    description: `E2E log exercise description ${logSequence}`,
    pageNumber: `${logSequence}`,
    tagName,
  };
}

function createLogEntry(bookTitle: string, section: Section, exercise: Exercise): LogEntry {
  logSequence += 1;

  return {
    bookTitle,
    sectionTitle: section.title,
    sectionName: exercise.sectionName,
    exerciseName: `${exercise.sectionName} #${exercise.identifier}`,
    pageNumber: exercise.pageNumber,
    practicedOn: '2026-05-11',
    tempo: `${90 + logSequence}`,
    notes: `${LOG_NOTES_PREFIX}${logSequence}`,
  };
}

test.describe('Logs page', () => {
  test.describe.configure({ mode: 'serial' });
  let authorPage: AuthorPage;
  let bookPage: BookPage;
  let sectionPage: SectionPage;
  let tagPage: TagPage;
  let exercisePage: ExercisePage;
  let logPage: LogPage;
  let book: Book;
  let section: Section;
  let exercise: Exercise;
  let tagName: string;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    bookPage = new BookPage(page);
    sectionPage = new SectionPage(page);
    tagPage = new TagPage(page);
    exercisePage = new ExercisePage(page);
    logPage = new LogPage(page);

    await logPage.deleteAllLogs(LOG_NOTES_PREFIX);
    await exercisePage.deleteAllExercises(LOG_EXERCISE_IDENTIFIER_PREFIX);
    await sectionPage.deleteAllSections(LOG_SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(LOG_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(LOG_AUTHOR_FIRST_NAME_PREFIX);
    await tagPage.deleteAllTags(LOG_TAG_NAME_PREFIX);

    const author = createAuthor();
    await authorPage.goto();
    await authorPage.addAuthor(author.firstName, author.lastName);

    book = createBook(`${author.firstName} ${author.lastName}`);
    await bookPage.goto();
    await bookPage.addBook(book);

    section = createSection(book.title);
    await sectionPage.goto();
    await sectionPage.addSection(section);

    tagName = `${LOG_TAG_NAME_PREFIX}${logSequence}`;
    await tagPage.goto();
    await tagPage.addTag(tagName);

    exercise = createExercise(`${section.bookTitle} - ${section.title}`, tagName);
    await exercisePage.goto();
    await exercisePage.addExercise(exercise);

    await logPage.goto();
  });

  test.afterEach(async () => {
    await logPage.deleteAllLogs(LOG_NOTES_PREFIX);
    await exercisePage.deleteAllExercises(LOG_EXERCISE_IDENTIFIER_PREFIX);
    await sectionPage.deleteAllSections(LOG_SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(LOG_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(LOG_AUTHOR_FIRST_NAME_PREFIX);
    await tagPage.deleteAllTags(LOG_TAG_NAME_PREFIX);
  });

  test('adds a log entry and shows it in the table', async () => {
    const logEntry = createLogEntry(book.title, section, exercise);

    await logPage.addLog(logEntry);

    await expect(logPage.getRow(logEntry)).toBeVisible();
  });

  test('does not create a log entry if tempo is missing', async () => {
    const logEntry = createLogEntry(book.title, section, exercise);

    await logPage.createBookSelect.selectOption({ label: logEntry.bookTitle });
    await expect(logPage.createSectionSelect.locator('option', { hasText: logEntry.sectionName })).toHaveCount(1);
    await logPage.createSectionSelect.selectOption({ label: logEntry.sectionName });
    await expect(logPage.createExerciseSelect.locator('option', { hasText: logEntry.exerciseName })).toHaveCount(1);
    await logPage.createExerciseSelect.selectOption({ label: logEntry.exerciseName });
    await logPage.createDateInput.fill(logEntry.practicedOn);
    await logPage.createNotesInput.fill(logEntry.notes);
    await logPage.createSubmitButton.click();

    await expect(logPage.getRowsByNotesPrefix(LOG_NOTES_PREFIX)).toHaveCount(0);
  });

  test('shows inline inputs when Edit is clicked', async () => {
    const logEntry = createLogEntry(book.title, section, exercise);

    await logPage.addLog(logEntry);

    const row = await logPage.openEdit(logEntry);

    await expect(row.locator('select[name="book"]')).toBeVisible();
    await expect(row.locator('select[name="exercise"]')).toBeVisible();
    await expect(row.locator('input[name="tempo"]')).toBeVisible();
    await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
  });

  test('saves updated log details', async () => {
    const logEntry = createLogEntry(book.title, section, exercise);
    const updatedLogEntry = createLogEntry(book.title, section, exercise);

    await logPage.addLog(logEntry);
    await logPage.editLog(logEntry, updatedLogEntry);

    await expect(logPage.getRow(updatedLogEntry)).toBeVisible();
    await expect(logPage.getRow(logEntry)).toHaveCount(0);
  });

  test('removes a deleted test-created log from the table', async () => {
    const logEntry = createLogEntry(book.title, section, exercise);

    await logPage.addLog(logEntry);
    await logPage.deleteLog(logEntry);

    await expect(logPage.getRow(logEntry)).toHaveCount(0);
  });
});
