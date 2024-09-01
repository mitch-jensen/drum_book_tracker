import pytest
from book_tracker.models import Author, Book, Section, Exercise
from asgiref.sync import sync_to_async


@pytest.mark.django_db
async def test_create_author():
    author = await Author.objects.acreate(first_name="George", last_name="Stone")
    assert author.first_name == "George"
    assert author.last_name == "Stone"


@pytest.mark.django_db
async def test_create_book():
    book = await Book.objects.acreate(title="Stick Control")
    book.title == "Stick Control"


@pytest.mark.django_db
async def test_create_section():
    book = await Book.objects.acreate(title="Stick Control")
    section = await Section.objects.acreate(book=book, title="Chapter 1", order=1)
    assert section.title == "Chapter 1"


@pytest.mark.django_db
async def test_create_exercise():
    book = await Book.objects.acreate(title="Stick Control")
    section = await Section.objects.acreate(book=book, title="Chapter 1", order=1)
    exercise = await Exercise.objects.acreate(
        section=section, title="Exercise 1", exercise_number=1
    )
    assert exercise.title == "Exercise 1"


@pytest.mark.django_db
async def test_create_tag():
    book = await Book.objects.acreate(title="Stick Control")
    await sync_to_async(book.tags.add)("Paradiddles")
    assert await book.tags.acount() == 1
