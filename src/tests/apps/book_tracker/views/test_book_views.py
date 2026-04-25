from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import Book
from tests.factories import AuthorFactory, BookFactory

if TYPE_CHECKING:
    from django.test import Client

    from book_tracker.models import Author

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestBookList:
    def test_renders_page(self, client: Client) -> None:
        response = client.get(reverse("book-list"))

        assert response.status_code == HTTPStatus.OK
        assert b"Books" in response.content

    def test_lists_existing_books(self, client: Client) -> None:
        author = AuthorFactory.create(first_name="George", last_name="Stone")
        BookFactory.create(title="Stick Control", page_count=190, authors=[author])

        response = client.get(reverse("book-list"))

        assert b"Stick Control" in response.content
        assert b"190" in response.content
        assert b"George Stone" in response.content

    def test_shows_empty_state(self, client: Client) -> None:
        response = client.get(reverse("book-list"))

        assert b"No books yet." in response.content

    def test_contains_create_form(self, client: Client) -> None:
        response = client.get(reverse("book-list"))

        assert b'hx-post="' in response.content
        assert b"Add Book" in response.content
        assert b"title" in response.content
        assert b"page_count" in response.content


class TestBookCreate:
    def test_creates_book(self, client: Client) -> None:
        author: Author = AuthorFactory.create()

        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "190", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert Book.objects.filter(title="Stick Control").exists()

    def test_success_retargets_to_full_list(self, client: Client) -> None:
        author: Author = AuthorFactory.create()

        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "190", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response["HX-Retarget"] == "#book-list-container"
        assert response["HX-Reswap"] == "innerHTML"

    def test_success_renders_new_book_in_list(self, client: Client) -> None:
        author: Author = AuthorFactory.create(first_name="George", last_name="Stone")

        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "190", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert b"Stick Control" in response.content
        assert b"George Stone" in response.content

    def test_validation_error_missing_title(self, client: Client) -> None:
        author: Author = AuthorFactory.create()

        response = client.post(
            reverse("book-create"),
            {"title": "", "page_count": "190", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Book.objects.exists()
        assert b"This field is required." in response.content

    def test_validation_error_missing_page_count(self, client: Client) -> None:
        author: Author = AuthorFactory.create()

        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Book.objects.exists()

    def test_validation_error_missing_authors(self, client: Client) -> None:
        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "190"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Book.objects.exists()

    def test_rejects_non_htmx_request(self, client: Client) -> None:
        author: Author = AuthorFactory.create()

        response = client.post(
            reverse("book-create"),
            {"title": "Stick Control", "page_count": "190", "authors": [str(author.pk)]},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_rejects_get_request(self, client: Client) -> None:
        response = client.get(reverse("book-create"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TestBookRow:
    def test_renders_book_row(self, client: Client, book: Book) -> None:
        response = client.get(reverse("book-row", args=[book.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"Stick Control" in response.content

    def test_returns_404_for_missing_book(self, client: Client) -> None:
        response = client.get(
            reverse("book-row", args=["00000000-0000-0000-0000-000000000000"]),
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_rejects_non_htmx_request(self, client: Client, book: Book) -> None:
        response = client.get(reverse("book-row", args=[book.pk]))

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestBookEdit:
    def test_renders_edit_form(self, client: Client, book: Book) -> None:
        response = client.get(reverse("book-edit", args=[book.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"Stick Control" in response.content
        assert b"Save" in response.content
        assert b"Cancel" in response.content

    def test_edit_form_contains_inputs(self, client: Client, book: Book) -> None:
        response = client.get(reverse("book-edit", args=[book.pk]), **HTMX_HEADERS)

        assert b'name="title"' in response.content
        assert b'name="page_count"' in response.content
        assert b'name="authors"' in response.content


class TestBookUpdate:
    def test_updates_book(self, client: Client, book: Book) -> None:
        author = book.authors.first()
        assert author is not None

        response = client.post(
            reverse("book-update", args=[book.pk]),
            {"title": "Advanced Stick Control", "page_count": "250", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        book.refresh_from_db()
        assert book.title == "Advanced Stick Control"
        assert book.page_count == 250

    def test_success_renders_updated_row(self, client: Client, book: Book) -> None:
        author = book.authors.first()
        assert author is not None

        response = client.post(
            reverse("book-update", args=[book.pk]),
            {"title": "Advanced Stick Control", "page_count": "250", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert b"Advanced Stick Control" in response.content

    def test_validation_error_returns_edit_form(self, client: Client, book: Book) -> None:
        author = book.authors.first()
        assert author is not None

        response = client.post(
            reverse("book-update", args=[book.pk]),
            {"title": "", "page_count": "190", "authors": [str(author.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        book.refresh_from_db()
        assert book.title == "Stick Control"  # unchanged
        assert b"This field is required." in response.content

    def test_returns_404_for_missing_book(self, client: Client) -> None:
        response = client.post(
            reverse("book-update", args=["00000000-0000-0000-0000-000000000000"]),
            {"title": "Foo", "page_count": "100", "authors": []},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
