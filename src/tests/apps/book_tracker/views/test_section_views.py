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

    def test_list_links_to_bulk_create(self, client: Client) -> None:
        response = client.get(reverse("section-list"))

        assert response.status_code == HTTPStatus.OK
        assert reverse("section-bulk-create").encode() in response.content

    def test_list_renders_sortable_section_handles(self, client: Client) -> None:
        book = BookFactory.create(title="Stick Control")
        SectionFactory.create(book=book, title="Warmups", order=1)
        SectionFactory.create(book=book, title="Rolls", order=2)

        response = client.get(reverse("section-list"))

        assert response.status_code == HTTPStatus.OK
        assert b'class="list-group sortable"' in response.content
        assert b'hx-trigger="end"' in response.content
        assert b"section-drag-handle" in response.content
        assert b"data-sortable-section" in response.content

    def test_row_and_edit_render_for_existing_section(self, client: Client) -> None:
        section = SectionFactory.create(title="Chapter 1", order=1)

        row_response = client.get(reverse("section-row", args=[section.pk]), **HTMX_HEADERS)
        edit_response = client.get(reverse("section-edit", args=[section.pk]), **HTMX_HEADERS)

        assert row_response.status_code == HTTPStatus.OK
        assert edit_response.status_code == HTTPStatus.OK
        assert b"Chapter 1" in row_response.content
        assert b"Save" in edit_response.content

    def test_update_success_and_validation_error_paths(self, client: Client) -> None:
        section = SectionFactory.create(title="Chapter 1", order=1)

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
        assert error.status_code == HTTPStatus.BAD_REQUEST
        assert b"This field is required." in error.content


class TestSectionBulkCreate:
    def test_get_renders_bulk_create_page(self, client: Client) -> None:
        response = client.get(reverse("section-bulk-create"))

        assert response.status_code == HTTPStatus.OK
        assert b"Bulk Create Sections" in response.content
        assert b"id_book" in response.content
        assert b"section_title" in response.content
        assert b"section_order" not in response.content

    def test_creates_multiple_sections_for_one_book(self, client: Client) -> None:
        book = BookFactory.create(title="Stick Control")

        response = client.post(
            reverse("section-bulk-create"),
            {
                "book": str(book.pk),
                "section_title": ["Warmups", "Rolls", "Flams"],
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert list(
            Section.objects.filter(book=book).order_by("order").values_list("title", "order"),
        ) == [("Warmups", 1), ("Rolls", 2), ("Flams", 3)]

    def test_missing_row_values_shows_error(self, client: Client) -> None:
        book = BookFactory.create(title="Stick Control")

        response = client.post(
            reverse("section-bulk-create"),
            {
                "book": str(book.pk),
                "section_title": ["Warmups", ""],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"title is required" in response.content
        assert not Section.objects.filter(book=book).exists()

    def test_appends_orders_after_existing_book_sections(self, client: Client) -> None:
        book = BookFactory.create(title="Stick Control")
        SectionFactory.create(book=book, title="Existing", order=2)

        response = client.post(
            reverse("section-bulk-create"),
            {
                "book": str(book.pk),
                "section_title": ["Warmups", "Rolls"],
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert list(
            Section.objects.filter(book=book).order_by("order").values_list("title", "order"),
        ) == [("Existing", 2), ("Warmups", 3), ("Rolls", 4)]

    def test_reorder_updates_section_orders_for_one_book(self, client: Client) -> None:
        book = BookFactory.create(title="Stick Control")
        first = SectionFactory.create(book=book, title="Warmups", order=1)
        second = SectionFactory.create(book=book, title="Rolls", order=2)
        third = SectionFactory.create(book=book, title="Flams", order=3)

        response = client.post(
            reverse("section-reorder"),
            {"section": [str(third.pk), str(first.pk), str(second.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert list(
            Section.objects.filter(book=book).order_by("order").values_list("title", "order"),
        ) == [("Flams", 1), ("Warmups", 2), ("Rolls", 3)]

    def test_reorder_rejects_sections_from_multiple_books(self, client: Client) -> None:
        first = SectionFactory.create(title="Warmups", order=1)
        second = SectionFactory.create(title="Rolls", order=1)

        response = client.post(
            reverse("section-reorder"),
            {"section": [str(first.pk), str(second.pk)]},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestSectionFormRow:
    def test_returns_row_partial(self, client: Client) -> None:
        response = client.get(reverse("section-form-row"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"section-form-row" in response.content
        assert b"section_title" in response.content
        assert b"section_order" not in response.content

    def test_requires_htmx(self, client: Client) -> None:
        response = client.get(reverse("section-form-row"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
