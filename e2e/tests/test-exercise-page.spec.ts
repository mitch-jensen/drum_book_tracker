import { test, expect } from '@playwright/test';
import { AuthorPage } from './playwright-author-page';
import { type Book, BookPage } from './playwright-book-page';
import { type Exercise, ExercisePage } from './playwright-exercise-page';
import { type Section, SectionPage } from './playwright-section-page';
import { TagPage } from './playwright-tag-page';

let exerciseSequence = 0;
const EXERCISE_AUTHOR_FIRST_NAME_PREFIX = 'E2EExerciseAuthorFirst';
const EXERCISE_BOOK_TITLE_PREFIX = 'E2E Exercise Book';
const EXERCISE_SECTION_TITLE_PREFIX = 'E2E Exercise Section';
const EXERCISE_IDENTIFIER_PREFIX = 'E2EEx';
const EXERCISE_TAG_NAME_PREFIX = 'E2EExerciseTag';

function createAuthor() {
  exerciseSequence += 1;

  return {
    firstName: `${EXERCISE_AUTHOR_FIRST_NAME_PREFIX}${exerciseSequence}`,
    lastName: `E2EExerciseAuthorLast${exerciseSequence}`,
  };
}

function createBook(authorName: string): Book {
  exerciseSequence += 1;

  return {
    title: `${EXERCISE_BOOK_TITLE_PREFIX} ${exerciseSequence}`,
    pageCount: `${140 + exerciseSequence}`,
    authorName,
  };
}

function createSection(bookTitle: string): Section {
  exerciseSequence += 1;

  return {
    bookTitle,
    title: `${EXERCISE_SECTION_TITLE_PREFIX} ${exerciseSequence}`,
    order: `${exerciseSequence}`,
  };
}

function createExercise(sectionName: string, tagName: string): Exercise {
  exerciseSequence += 1;

  return {
    sectionName,
    identifier: `${EXERCISE_IDENTIFIER_PREFIX}${exerciseSequence}`,
    description: `E2E exercise description ${exerciseSequence}`,
    pageNumber: `${exerciseSequence}`,
    tagName,
  };
}

test.describe('Exercises page', () => {
  test.describe.configure({ mode: 'serial' });
  let authorPage: AuthorPage;
  let bookPage: BookPage;
  let sectionPage: SectionPage;
  let tagPage: TagPage;
  let exercisePage: ExercisePage;
  let section: Section;
  let sectionName: string;
  let tagName: string;

  test.beforeEach(async ({ page }) => {
    authorPage = new AuthorPage(page);
    bookPage = new BookPage(page);
    sectionPage = new SectionPage(page);
    tagPage = new TagPage(page);
    exercisePage = new ExercisePage(page);

    await exercisePage.deleteAllExercises(EXERCISE_IDENTIFIER_PREFIX);
    await sectionPage.deleteAllSections(EXERCISE_SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(EXERCISE_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(EXERCISE_AUTHOR_FIRST_NAME_PREFIX);
    await tagPage.deleteAllTags(EXERCISE_TAG_NAME_PREFIX);

    const author = createAuthor();
    await authorPage.goto();
    await authorPage.addAuthor(author.firstName, author.lastName);

    const book = createBook(`${author.firstName} ${author.lastName}`);
    await bookPage.goto();
    await bookPage.addBook(book);

    section = createSection(book.title);
    await sectionPage.goto();
    await sectionPage.addSection(section);
    sectionName = `${section.bookTitle} - ${section.title}`;

    tagName = `${EXERCISE_TAG_NAME_PREFIX}${exerciseSequence}`;
    await tagPage.goto();
    await tagPage.addTag(tagName);

    await exercisePage.goto();
  });

  test.afterEach(async () => {
    await exercisePage.deleteAllExercises(EXERCISE_IDENTIFIER_PREFIX);
    await sectionPage.deleteAllSections(EXERCISE_SECTION_TITLE_PREFIX);
    await bookPage.deleteAllBooks(EXERCISE_BOOK_TITLE_PREFIX);
    await authorPage.deleteAllAuthors(EXERCISE_AUTHOR_FIRST_NAME_PREFIX);
    await tagPage.deleteAllTags(EXERCISE_TAG_NAME_PREFIX);
  });

  test('adds an exercise and shows it in the table', async () => {
    const exercise = createExercise(sectionName, tagName);

    await exercisePage.addExercise(exercise);

    await expect(exercisePage.getRow(exercise)).toBeVisible();
  });

  test('does not create an exercise if identifier and description are missing', async () => {
    const exercise = createExercise(sectionName, tagName);

    await exercisePage.createSectionSelect.selectOption({ label: exercise.sectionName });
    await exercisePage.createPageNumberInput.fill(exercise.pageNumber);
    await exercisePage.createTagsSelect.selectOption({ label: exercise.tagName });
    await exercisePage.createSubmitButton.click();

    await expect(exercisePage.getRowsByIdentifierPrefix(EXERCISE_IDENTIFIER_PREFIX)).toHaveCount(0);
  });

  test('shows inline inputs when Edit is clicked', async () => {
    const exercise = createExercise(sectionName, tagName);

    await exercisePage.addExercise(exercise);

    const row = await exercisePage.openEdit(exercise);

    await expect(row.locator('select[name="section"]')).toBeVisible();
    await expect(row.getByRole('textbox').first()).toBeVisible();
    await expect(row.getByRole('spinbutton')).toBeVisible();
    await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
  });

  test('saves updated exercise details', async () => {
    const exercise = createExercise(sectionName, tagName);
    const updatedExercise = createExercise(sectionName, tagName);

    await exercisePage.addExercise(exercise);
    await exercisePage.editExercise(exercise, updatedExercise);

    await expect(exercisePage.getRow(updatedExercise)).toBeVisible();
    await expect(exercisePage.getRow(exercise)).toHaveCount(0);
  });

  test('removes a deleted test-created exercise from the table', async () => {
    const exercise = createExercise(sectionName, tagName);

    await exercisePage.addExercise(exercise);
    await exercisePage.deleteExercise(exercise);

    await expect(exercisePage.getRow(exercise)).toHaveCount(0);
  });
});
