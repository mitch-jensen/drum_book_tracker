from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import Section
from tests.factories import BookFactory, SectionFactory

if TYPE_CHECKING:
    from django.test import Client


pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestSectionViews:
    def test_list_renders_sections_page(self, client: Client) -> None:
        response = client.get(reverse("section-list"))

        assert response.status_code == HTTPStatus.OK
        assert b"Sections" in response.content

    def test_create_success_returns_list_partial(self, client: Client) -> None:
        book = BookFactory(title="Stick Control")

        response = client.post(
            reverse("section-create"),
            {"book": str(book.pk), "title": "Chapter 1", "order": "1"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert response["HX-Retarget"] == "#section-list-container"
        assert response["HX-Reswap"] == "innerHTML"
        assert Section.objects.filter(book=book, title="Chapter 1", order=1).exists()

    def test_create_validation_error_returns_form_partial(self, client: Client) -> None:
        response = client.post(
            reverse("section-create"),
            {"book": "", "title": "", "order": ""},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert b"This field is required." in response.content

    def test_row_and_edit_render_for_existing_section(self, client: Client) -> None:
        section = SectionFactory(title="Chapter 1", order=1)

        row_response = client.get(reverse("section-row", args=[section.pk]), **HTMX_HEADERS)
        edit_response = client.get(reverse("section-edit", args=[section.pk]), **HTMX_HEADERS)

        assert row_response.status_code == HTTPStatus.OK
        assert edit_response.status_code == HTTPStatus.OK
        assert b"Chapter 1" in row_response.content
        assert b"Save" in edit_response.content

    def test_update_success_and_validation_error_paths(self, client: Client) -> None:
        section = SectionFactory(title="Chapter 1", order=1)

        success = client.post(
            reverse("section-update", args=[section.pk]),
            {"book": str(section.book_id), "title": "Warmups", "order": "2"},
            **HTMX_HEADERS,
        )
        section.refresh_from_db()

        error = client.post(
            reverse("section-update", args=[section.pk]),
            {"book": str(section.book_id), "title": "", "order": "2"},
            **HTMX_HEADERS,
        )

        assert success.status_code == HTTPStatus.OK
        assert section.title == "Warmups"
        assert section.order == 2
        assert error.status_code == HTTPStatus.OK
        assert b"This field is required." in error.content
