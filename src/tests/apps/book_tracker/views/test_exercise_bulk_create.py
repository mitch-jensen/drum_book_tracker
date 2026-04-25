from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import Exercise
from tests.factories import ExerciseFactory, SectionFactory, TagFactory

if TYPE_CHECKING:
    from django.test import Client

    from book_tracker.models import Section, Tag

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestExerciseBulkCreateGet:
    def test_renders_page(self, client: Client) -> None:
        response = client.get(reverse("exercise-bulk-create"))

        assert response.status_code == HTTPStatus.OK
        assert b"Bulk Create Exercises" in response.content

    def test_contains_form_fields(self, client: Client) -> None:
        response = client.get(reverse("exercise-bulk-create"))

        assert b"id_section" in response.content
        assert b"id_start" in response.content
        assert b"id_end" in response.content
        assert b"id_tags" in response.content

    def test_contains_page_range_row(self, client: Client) -> None:
        response = client.get(reverse("exercise-bulk-create"))

        assert b"range_start" in response.content
        assert b"range_end" in response.content
        assert b"range_page" in response.content


class TestExerciseBulkCreatePost:
    def test_creates_exercises(self, client: Client) -> None:
        section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 5,
                "range_start": ["1"],
                "range_end": ["5"],
                "range_page": ["10"],
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert Exercise.objects.filter(section=section).count() == 5
        for i in range(1, 6):
            ex = Exercise.objects.get(section=section, identifier=str(i))
            assert ex.page_number == 10

    def test_creates_exercises_with_multiple_page_ranges(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 10,
                "range_start": ["1", "6"],
                "range_end": ["5", "10"],
                "range_page": ["20", "21"],
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        assert Exercise.objects.filter(section=section).count() == 10
        assert Exercise.objects.get(section=section, identifier="3").page_number == 20
        assert Exercise.objects.get(section=section, identifier="8").page_number == 21

    def test_applies_tags_to_all_exercises(self, client: Client) -> None:
        section: Section = SectionFactory.create()
        tag1: Tag = TagFactory.create(name="Singles")
        tag2: Tag = TagFactory.create(name="Doubles")

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 3,
                "tags": [tag1.pk, tag2.pk],
                "range_start": ["1"],
                "range_end": ["3"],
                "range_page": ["5"],
            },
        )

        assert response.status_code == HTTPStatus.FOUND
        for i in range(1, 4):
            ex = Exercise.objects.get(section=section, identifier=str(i))
            assert set(ex.tags.values_list("name", flat=True)) == {"Singles", "Doubles"}

    def test_start_greater_than_end_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 5,
                "end": 1,
                "range_start": ["5"],
                "range_end": ["1"],
                "range_page": ["10"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"Start must be less than or equal to end" in response.content
        assert Exercise.objects.count() == 0

    def test_page_range_from_greater_than_to_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 5,
                "range_start": ["4"],
                "range_end": ["2"],
                "range_page": ["10"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"must be" in response.content
        assert b"to" in response.content
        assert Exercise.objects.count() == 0

    def test_conflicting_identifiers_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()
        ExerciseFactory.create(section=section, identifier="3")

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 5,
                "range_start": ["1"],
                "range_end": ["5"],
                "range_page": ["10"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"already exist" in response.content
        # Only the pre-existing exercise should remain
        assert Exercise.objects.filter(section=section).count() == 1

    def test_overlapping_page_ranges_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 10,
                "range_start": ["1", "4"],
                "range_end": ["5", "10"],
                "range_page": ["20", "21"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"overlap" in response.content
        assert Exercise.objects.count() == 0

    def test_incomplete_coverage_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 10,
                "range_start": ["1"],
                "range_end": ["5"],
                "range_page": ["20"],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"do not cover" in response.content
        assert Exercise.objects.count() == 0

    def test_missing_page_range_fields_shows_error(self, client: Client) -> None:
        section: Section = SectionFactory.create()

        response = client.post(
            reverse("exercise-bulk-create"),
            {
                "section": section.pk,
                "start": 1,
                "end": 3,
                "range_start": ["1"],
                "range_end": ["3"],
                "range_page": [""],
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert b"all fields are required" in response.content
        assert Exercise.objects.count() == 0


class TestPageRangeRow:
    def test_returns_row_partial(self, client: Client) -> None:
        response = client.get(reverse("page-range-row"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert b"range_start" in response.content
        assert b"page-range-row" in response.content

    def test_requires_htmx(self, client: Client) -> None:
        response = client.get(reverse("page-range-row"))

        assert response.status_code == HTTPStatus.BAD_REQUEST
