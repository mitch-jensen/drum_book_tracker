import { test, expect } from '@playwright/test';
import { TagPage } from './playwright-tag-page';

let tagSequence = 0;

function createTagName(): string {
  tagSequence += 1;

  return `E2ETag${tagSequence}`;
}

test.describe('Tags page', () => {
  test.describe.configure({ mode: 'serial' });
  let tagPage: TagPage;

  test.beforeEach(async ({ page }) => {
    tagPage = new TagPage(page);
    await tagPage.goto();
  });

  test.afterEach(async () => {
    await tagPage.deleteAllTags();
  });

  test.describe('adding a tag', () => {
    test('adds a single tag and shows it in the table', async () => {
      const tagName = createTagName();

      await tagPage.addTag(tagName);

      await expect(tagPage.getRow(tagName)).toBeVisible();
    });

    test('adds multiple tags and shows them in the table', async () => {
      const tagName = createTagName();
      const secondTagName = createTagName();

      await tagPage.addTag(tagName);
      await tagPage.addTag(secondTagName);

      await expect(tagPage.getRow(tagName)).toBeVisible();
      await expect(tagPage.getRow(secondTagName)).toBeVisible();
    });

    test('clears the form after a successful submission', async () => {
      const tagName = createTagName();

      await tagPage.addTag(tagName);

      await expect(tagPage.createNameInput).toHaveValue('');
    });
  });

  test.describe('add tag form validation', () => {
    test('does not create a tag if name is missing', async () => {
      await tagPage.createSubmitButton.click();

      await expect(tagPage.getAllRows()).toHaveCount(0);
    });
  });

  test.describe('editing a tag', () => {
    test('shows inline input when Edit is clicked', async () => {
      const tagName = createTagName();

      await tagPage.addTag(tagName);

      const row = await tagPage.openEdit(tagName);

      await expect(row.getByRole('textbox')).toBeVisible();
      await expect(row.getByRole('button', { name: /save/i })).toBeVisible();
      await expect(row.getByRole('button', { name: /cancel/i })).toBeVisible();
    });

    test('saves updated tag details', async () => {
      const tagName = createTagName();
      const updatedTagName = createTagName();

      await tagPage.addTag(tagName);
      await tagPage.editTag(tagName, updatedTagName);

      await expect(tagPage.getRow(updatedTagName)).toBeVisible();
      await expect(tagPage.getRow(tagName)).toHaveCount(0);
    });
  });

  test.describe('tags table', () => {
    test('shows no test-created tag on a fresh page', async () => {
      const tags = await tagPage.getAllTags();

      expect(tags).toHaveLength(0);
    });

    test('shows the empty-state message when there are no tag rows', async () => {
      await expect(tagPage.tbody).toContainText(/no tags yet/i);
    });

    test('shows the empty-state message after deleting the last tag', async () => {
      const tagName = createTagName();

      await tagPage.addTag(tagName);
      await tagPage.deleteTag(tagName);

      const tags = await tagPage.getAllTags();

      expect(tags).toHaveLength(0);
      await expect(tagPage.tbody).toContainText(/no tags yet/i);
    });
  });
});
