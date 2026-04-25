from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import Tag
from tests.factories import TagFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestTagList:
    def test_renders_page(self, client: Client) -> None:
        response = client.get(reverse("tag-list"))

        assert response.status_code == HTTPStatus.OK
        assert b"Tags" in response.content

    def test_lists_existing_tags(self, client: Client) -> None:
        TagFactory.create(name="rudiment")
        TagFactory.create(name="groove")

        response = client.get(reverse("tag-list"))

        assert b"rudiment" in response.content
        assert b"groove" in response.content

    def test_shows_empty_state(self, client: Client) -> None:
        response = client.get(reverse("tag-list"))

        assert b"No tags yet." in response.content

    def test_contains_create_form(self, client: Client) -> None:
        response = client.get(reverse("tag-list"))

        assert b'hx-post="' in response.content
        assert b"Add Tag" in response.content
        assert b"name" in response.content


class TestTagCreate:
    def test_creates_tag(self, client: Client) -> None:
        response = client.post(
            reverse("tag-create"),
            {"name": "paradiddle"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert Tag.objects.filter(name="paradiddle").exists()

    def test_success_retargets_to_full_list(self, client: Client) -> None:
        response = client.post(
            reverse("tag-create"),
            {"name": "paradiddle"},
            **HTMX_HEADERS,
        )

        assert response["HX-Retarget"] == "#tag-list-container"
        assert response["HX-Reswap"] == "innerHTML"

    def test_success_renders_new_tag_in_list(self, client: Client) -> None:
        response = client.post(
            reverse("tag-create"),
            {"name": "paradiddle"},
            **HTMX_HEADERS,
        )

        assert b"paradiddle" in response.content

    def test_validation_error_missing_name(self, client: Client) -> None:
        response = client.post(
            reverse("tag-create"),
            {"name": ""},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert not Tag.objects.exists()
        assert b"This field is required." in response.content

    def test_validation_error_duplicate_name(self, client: Client) -> None:
        TagFactory.create(name="rudiment")

        response = client.post(
            reverse("tag-create"),
            {"name": "rudiment"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        assert Tag.objects.filter(name="rudiment").count() == 1

    def test_rejects_non_htmx_request(self, client: Client) -> None:
        response = client.post(
            reverse("tag-create"),
            {"name": "paradiddle"},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_rejects_get_request(self, client: Client) -> None:
        response = client.get(reverse("tag-create"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TestTagRow:
    def test_renders_tag_row(self, client: Client, tag: Tag) -> None:
        response = client.get(reverse("tag-row", args=[tag.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"rudiment" in response.content

    def test_returns_404_for_missing_tag(self, client: Client) -> None:
        response = client.get(
            reverse("tag-row", args=["00000000-0000-0000-0000-000000000000"]),
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_rejects_non_htmx_request(self, client: Client, tag: Tag) -> None:
        response = client.get(reverse("tag-row", args=[tag.pk]))

        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestTagEdit:
    def test_renders_edit_form(self, client: Client, tag: Tag) -> None:
        response = client.get(reverse("tag-edit", args=[tag.pk]), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"rudiment" in response.content
        assert b"Save" in response.content
        assert b"Cancel" in response.content

    def test_edit_form_contains_name_input(self, client: Client, tag: Tag) -> None:
        response = client.get(reverse("tag-edit", args=[tag.pk]), **HTMX_HEADERS)

        assert b'name="name"' in response.content


class TestTagUpdate:
    def test_updates_tag(self, client: Client, tag: Tag) -> None:
        response = client.post(
            reverse("tag-update", args=[tag.pk]),
            {"name": "groove"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        tag.refresh_from_db()
        assert tag.name == "groove"

    def test_success_renders_updated_row(self, client: Client, tag: Tag) -> None:
        response = client.post(
            reverse("tag-update", args=[tag.pk]),
            {"name": "groove"},
            **HTMX_HEADERS,
        )

        assert b"groove" in response.content

    def test_validation_error_returns_edit_form(self, client: Client, tag: Tag) -> None:
        response = client.post(
            reverse("tag-update", args=[tag.pk]),
            {"name": ""},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.OK
        tag.refresh_from_db()
        assert tag.name == "rudiment"
        assert b"This field is required." in response.content

    def test_returns_404_for_missing_tag(self, client: Client) -> None:
        response = client.post(
            reverse("tag-update", args=["00000000-0000-0000-0000-000000000000"]),
            {"name": "groove"},
            **HTMX_HEADERS,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.fixture
def tag() -> Tag:
    return TagFactory.create(name="rudiment")  # pyrefly: ignore[bad-return]
