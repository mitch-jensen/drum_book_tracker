import pytest
from book_tracker.models import Author, Book

@pytest.mark.django_db
async def test_create_author():
    author = await Author.objects.acreate(first_name="George", last_name="Stone")
    assert author.first_name == "George"
    assert author.last_name == "Stone"

@pytest.mark.django_db
async def test_create_book():
    book = await Book.objects.acreate(title="Stick Control")
    book.title == "Stick Control"
    
