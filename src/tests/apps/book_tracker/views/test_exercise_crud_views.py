from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.http import QueryDict
from django.urls import reverse

from book_tracker.models import Exercise
from book_tracker.views import (
    PageRangeRowParseResult,
    _parse_page_range_row,
    _parse_page_ranges,
)
from tests.factories import ExerciseFactory, SectionFactory, TagFactory

if TYPE_CHECKING:
    from django.test import Client

    from book_tracker.models import Section, Tag

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestExerciseCrudViews:
    def test_create_success_and_validation_error_paths(self, client: Client) -> None:
        section: Section = SectionFactory.create()
        tag: Tag = TagFactory.create(name="rudiment")

        success = client.post(
            reverse("exercise-create"),
            {
                "section": str(section.pk),
                "identifier": "7",
                "description": "Accent warmup",
                "page_number": "15",
                "tags": [str(tag.pk)],
            },
            **HTMX_HEADERS,
        )
        error = client.post(
            reverse("exercise-create"),
            {
                "section": "",
                "identifier": "",
                "description": "",
                "page_number": "",
            },
            **HTMX_HEADERS,
        )

        assert success.status_code == HTTPStatus.OK
        assert success["HX-Retarget"] == "#exercise-list-container"
        assert success["HX-Reswap"] == "innerHTML"
        assert Exercise.objects.filter(section=section, identifier="7").exists()
        assert error.status_code == HTTPStatus.OK
        assert b"This field is required." in error.content

    def test_row_edit_and_update_paths(self, client: Client) -> None:
        exercise: Exercise = ExerciseFactory.create(identifier="1", description="Single strokes")

        row_response = client.get(reverse("exercise-row", args=[exercise.pk]), **HTMX_HEADERS)
        edit_response = client.get(reverse("exercise-edit", args=[exercise.pk]), **HTMX_HEADERS)
        update_success = client.post(
            reverse("exercise-update", args=[exercise.pk]),
            {
                "section": str(exercise.section_id),
                "identifier": "2",
                "description": "Double strokes",
                "page_number": "22",
            },
            **HTMX_HEADERS,
        )
        exercise.refresh_from_db()
        update_error = client.post(
            reverse("exercise-update", args=[exercise.pk]),
            {
                "section": str(exercise.section_id),
                "identifier": "",
                "description": "",
                "page_number": "22",
            },
            **HTMX_HEADERS,
        )

        assert row_response.status_code == HTTPStatus.OK
        assert edit_response.status_code == HTTPStatus.OK
        assert update_success.status_code == HTTPStatus.OK
        assert exercise.identifier == "2"
        assert update_error.status_code == HTTPStatus.OK
        assert b'name="identifier"' in update_error.content
        assert b'name="description"' in update_error.content


class TestExerciseBulkCreatePageRangeValidation:
    def test_requires_at_least_one_page_range(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": str(section.pk),
                "start": "1",
                "end": "3",
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"At least one page range is required." in response.content

    def test_rejects_non_integer_values_and_out_of_bounds_and_non_positive_pages(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": str(section.pk),
                "start": "1",
                "end": "5",
                "range_start": ["a", "0", "4"],
                "range_end": ["2", "1", "5"],
                "range_page": ["10", "10", "0"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "values must be integers" in content
        assert "outside exercises 1-5" in content
        assert "page number must be positive" in content

    def test_rehydrates_default_page_range_row_when_none_submitted(self, client: Client) -> None:
        response = client.post(reverse("exercise-bulk-create"), {})

        assert response.status_code == HTTPStatus.OK
        assert response.context is not None
        assert response.context["page_ranges"] == [("", "", "")]


class TestExerciseBulkCreatePageRangeTyping:
    def test_parse_page_range_row_returns_named_result(self) -> None:
        result = _parse_page_range_row(
            row_index=1,
            raw_start="1",
            raw_end="3",
            raw_page="10",
            exercise_start=1,
            exercise_end=5,
        )

        assert isinstance(result, PageRangeRowParseResult)
        assert result.page_range is not None
        assert result.page_range.start == 1
        assert result.page_range.end == 3
        assert result.page_range.page == 10
        assert result.error is None

    def test_parse_page_ranges_returns_typed_dict_result(self) -> None:
        post_data = QueryDict("", mutable=True)
        post_data.setlist("range_start", ["1"])
        post_data.setlist("range_end", ["3"])
        post_data.setlist("range_page", ["10"])

        result = _parse_page_ranges(
            post_data=post_data,
            start=1,
            end=3,
        )

        assert isinstance(result, dict)
        assert "page_lookup" in result
        assert isinstance(result["page_lookup"], dict)
        assert "exercise_to_page" in result["page_lookup"]
        assert result["page_lookup"]["exercise_to_page"] == {1: 10, 2: 10, 3: 10}

    def test_parse_page_ranges_returns_typed_error_dict(self) -> None:
        post_data = QueryDict("", mutable=True)
        post_data.setlist("range_start", ["1"])
        post_data.setlist("range_end", ["2"])
        post_data.setlist("range_page", ["10"])

        result = _parse_page_ranges(
            post_data=post_data,
            start=1,
            end=3,
        )

        assert isinstance(result, dict)
        assert "errors" in result
        assert isinstance(result["errors"], list)
        assert "do not cover exercises" in result["errors"][0]
