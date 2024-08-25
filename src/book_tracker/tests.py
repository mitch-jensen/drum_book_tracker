import pytest
from book_tracker.models import Book

@pytest.mark.django_db
class TestBookModel:
    def test_create_book(self):
        book = Book.objects.create(title="Stick Control", author="George Lawrence Stone")
        assert book.title == "Stick Control"
        assert book.author == "George Lawrence Stone"
        assert Book.objects.count() == 1
