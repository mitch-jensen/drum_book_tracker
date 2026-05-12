from http import HTTPStatus  # noqa: INP001
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django.test import Client

    from book_tracker.models import Book

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}
TEMPLATE_ROOT = Path("src/book_tracker/templates/book_tracker")


def _template_names(response: object) -> set[str]:
    templates = getattr(response, "templates", [])
    return {template.name for template in templates if getattr(template, "name", None)}


@pytest.mark.parametrize(
    ("view_name", "expected_template"),
    [
        ("author-list", "book_tracker/authors/list.html"),
        ("tag-list", "book_tracker/tags/list.html"),
        ("book-list", "book_tracker/books/list.html"),
        ("section-list", "book_tracker/sections/list.html"),
        ("exercise-list", "book_tracker/exercises/list.html"),
        ("log-list", "book_tracker/logs/list.html"),
    ],
)
def test_list_pages_use_feature_page_templates(
    client: Client,
    view_name: str,
    expected_template: str,
) -> None:
    response = client.get(reverse(view_name))

    assert response.status_code == HTTPStatus.OK
    assert expected_template in _template_names(response)


def test_author_create_success_uses_authors_list_partial(client: Client) -> None:
    response = client.post(
        reverse("author-create"),
        {"first_name": "George", "last_name": "Stone"},
        **HTMX_HEADERS,
    )

    assert response.status_code == HTTPStatus.OK
    assert "book_tracker/authors/_list.html" in _template_names(response)


def test_author_create_validation_error_uses_authors_form_partial(client: Client) -> None:
    response = client.post(
        reverse("author-create"),
        {"first_name": "", "last_name": "Stone"},
        **HTMX_HEADERS,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "book_tracker/authors/_create_form.html" in _template_names(response)


def test_book_row_uses_books_row_partial(client: Client, book: Book) -> None:
    response = client.get(reverse("book-row", args=[book.pk]), **HTMX_HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert "book_tracker/books/_row.html" in _template_names(response)


def test_section_options_uses_logs_section_options_partial(client: Client, book: Book) -> None:
    response = client.get(
        reverse("section-options"),
        {"book": str(book.pk)},
        **HTMX_HEADERS,
    )

    assert response.status_code == HTTPStatus.OK
    assert "book_tracker/logs/_section_options.html" in _template_names(response)


def test_exercise_options_uses_logs_exercise_options_partial(client: Client, book: Book) -> None:
    response = client.get(
        reverse("exercise-options"),
        {"book": str(book.pk)},
        **HTMX_HEADERS,
    )

    assert response.status_code == HTTPStatus.OK
    assert "book_tracker/logs/_exercise_options.html" in _template_names(response)


def test_page_range_row_uses_exercises_page_range_partial(client: Client) -> None:
    response = client.get(reverse("page-range-row"), **HTMX_HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert "book_tracker/exercises/_page_range_row.html" in _template_names(response)


def test_crud_templates_use_current_partial_names() -> None:
    stale_partials = [path for path in TEMPLATE_ROOT.glob("*/*.html") if path.name in {"_edit_row.html", "_form.html"}]

    assert stale_partials == []


@pytest.mark.parametrize(
    "template_path",
    [
        TEMPLATE_ROOT / "authors/_create_form.html",
        TEMPLATE_ROOT / "books/_create_form.html",
        TEMPLATE_ROOT / "exercises/_create_form.html",
        TEMPLATE_ROOT / "logs/_create_form.html",
        TEMPLATE_ROOT / "tags/_create_form.html",
    ],
)
def test_create_form_submit_buttons_align_with_fields(template_path: Path) -> None:
    template = template_path.read_text()

    assert "col-auto align-self-end" in template
