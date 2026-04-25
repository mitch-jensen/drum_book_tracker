from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import Author
from tests.factories import AuthorFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestAuthorList:
    def test_renders_page(self, client: Client) -> None:
        response = client.get(reverse("author-list"))

        assert response.status_code == HTTPStatus.OK
        assert b"Authors" in response.content

    def test_lists_existing_authors(self, client: Client) -> None:
        AuthorFactory.create(first_name="George", last_name="Stone")
        AuthorFactory.create(first_name="Ted", last_name="Reed")

        response = client.get(reverse("author-list"))

        assert b"George" in response.content
        assert b"Stone" in response.content
        assert b"Ted" in response.content
        assert b"Reed" in response.content

    def test_shows_empty_state(self, client: Client) -> None:
        response = client.get(reverse("author-list"))

        assert b"No authors yet." in response.content

    def test_contains_create_form(self, client: Client) -> None:
        response = client.get(reverse("author-list"))

        assert b'hx-post="' in response.content
        assert b"Add Author" in response.content
        assert b"first_name" in response.content
        assert b"last_name" in response.content


class TestAuthorCreate:
    def test_creates_author(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "George", "last_name": "Stone"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert Author.objects.filter(first_name="George", last_name="Stone").exists()

    def test_success_retargets_to_full_list(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "George", "last_name": "Stone"},
            **HTMX_HEADERS,
        )

        assert response["HX-Retarget"] == "#author-list-container"
        assert response["HX-Reswap"] == "innerHTML"

    def test_success_renders_new_author_in_list(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "George", "last_name": "Stone"},
            **HTMX_HEADERS,
        )

        assert b"George" in response.content
        assert b"Stone" in response.content

    def test_validation_error_missing_first_name(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "", "last_name": "Stone"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Author.objects.exists()
        assert b"This field is required." in response.content

    def test_validation_error_missing_last_name(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "George", "last_name": ""},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Author.objects.exists()

    def test_rejects_non_htmx_request(self, client: Client) -> None:
        response = client.post(
            reverse("author-create"),
            {"first_name": "George", "last_name": "Stone"},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_rejects_get_request(self, client: Client) -> None:
        response = client.get(reverse("author-create"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TestAuthorRow:
    def test_renders_author_row(self, client: Client, author: Author) -> None:
        response = client.get(reverse("author-row", args=[author.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"George" in response.content
        assert b"Stone" in response.content

    def test_returns_404_for_missing_author(self, client: Client) -> None:
        response = client.get(
            reverse("author-row", args=["00000000-0000-0000-0000-000000000000"]),
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_rejects_non_htmx_request(self, client: Client, author: Author) -> None:
        response = client.get(reverse("author-row", args=[author.pk]))

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestAuthorEdit:
    def test_renders_edit_form(self, client: Client, author: Author) -> None:
        response = client.get(reverse("author-edit", args=[author.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"George" in response.content
        assert b"Stone" in response.content
        assert b"Save" in response.content
        assert b"Cancel" in response.content

    def test_edit_form_contains_inputs(self, client: Client, author: Author) -> None:
        response = client.get(reverse("author-edit", args=[author.pk]), **HTMX_HEADERS)

        assert b'name="first_name"' in response.content
        assert b'name="last_name"' in response.content


class TestAuthorUpdate:
    def test_updates_author(self, client: Client, author: Author) -> None:
        response = client.post(
            reverse("author-update", args=[author.pk]),
            {"first_name": "Ted", "last_name": "Reed"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        author.refresh_from_db()
        assert author.first_name == "Ted"
        assert author.last_name == "Reed"

    def test_success_renders_updated_row(self, client: Client, author: Author) -> None:
        response = client.post(
            reverse("author-update", args=[author.pk]),
            {"first_name": "Ted", "last_name": "Reed"},
            **HTMX_HEADERS,
        )

        assert b"Ted" in response.content
        assert b"Reed" in response.content

    def test_validation_error_returns_edit_form(self, client: Client, author: Author) -> None:
        response = client.post(
            reverse("author-update", args=[author.pk]),
            {"first_name": "", "last_name": "Reed"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        author.refresh_from_db()
        assert author.first_name == "George"  # unchanged
        assert b"This field is required." in response.content

    def test_returns_404_for_missing_author(self, client: Client) -> None:
        response = client.post(
            reverse("author-update", args=["00000000-0000-0000-0000-000000000000"]),
            {"first_name": "Ted", "last_name": "Reed"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
