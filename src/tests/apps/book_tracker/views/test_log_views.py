import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import PracticeLog
from tests.factories import BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestLogOptionsViews:
    def test_section_options_without_book_returns_empty_sections(self, client: Client) -> None:
        response = client.get(reverse("section-options"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert response.context is not None
        assert list(response.context["sections"]) == []

    def test_exercise_options_without_book_returns_empty_exercises(self, client: Client) -> None:
        response = client.get(reverse("exercise-options"), **HTMX_HEADERS)

        assert response.status_code == HTTPStatus.OK
        assert response.context is not None
        assert list(response.context["exercises"]) == []


class TestPracticeLogCrudViews:
    def test_create_success_and_validation_error_paths(self, client: Client) -> None:
        book = BookFactory(page_count=100)
        section = SectionFactory(book=book, order=1)
        exercise = ExerciseFactory(section=section, identifier="1", page_number=7)

        success = client.post(
            reverse("log-create"),
            {
                "book": str(book.pk),
                "section": str(section.pk),
                "exercise": str(exercise.pk),
                "page_number": "7",
                "practiced_on": datetime.date(2026, 4, 23).isoformat(),
                "tempo": "110",
                "difficulty": str(PracticeLog.Difficulty.MEDIUM),
                "relaxation_level": str(PracticeLog.RelaxationLevel.NEUTRAL),
                "notes": "Clean run",
            },
            **HTMX_HEADERS,
        )
        invalid = client.post(
            reverse("log-create"),
            {
                "book": str(book.pk),
                "section": str(section.pk),
                "exercise": str(exercise.pk),
                "page_number": "7",
                "practiced_on": datetime.date(2026, 4, 23).isoformat(),
                "tempo": "",
                "difficulty": str(PracticeLog.Difficulty.MEDIUM),
                "relaxation_level": str(PracticeLog.RelaxationLevel.NEUTRAL),
                "notes": "",
            },
            **HTMX_HEADERS,
        )

        assert success.status_code == HTTPStatus.OK
        assert success["HX-Retarget"] == "#log-list-container"
        assert success["HX-Reswap"] == "innerHTML"
        assert success["HX-Trigger"] == "logCreated"
        assert PracticeLog.objects.filter(exercise=exercise, tempo=110).exists()
        assert invalid.status_code == HTTPStatus.OK
        assert b"This field is required." in invalid.content

    def test_row_edit_and_update_paths(self, client: Client) -> None:
        log = PracticeLogFactory(tempo=90)

        row_response = client.get(reverse("log-row", args=[log.pk]), **HTMX_HEADERS)
        edit_response = client.get(reverse("log-edit", args=[log.pk]), **HTMX_HEADERS)
        update_success = client.post(
            reverse("log-update", args=[log.pk]),
            {
                "book": str(log.exercise.section.book_id),
                "section": str(log.exercise.section_id),
                "exercise": str(log.exercise_id),
                "page_number": str(log.exercise.page_number or ""),
                "practiced_on": datetime.date(2026, 4, 24).isoformat(),
                "tempo": "120",
                "difficulty": str(PracticeLog.Difficulty.EASY),
                "relaxation_level": str(PracticeLog.RelaxationLevel.RELAXED),
                "notes": "Updated",
            },
            **HTMX_HEADERS,
        )
        log.refresh_from_db()
        update_error = client.post(
            reverse("log-update", args=[log.pk]),
            {
                "book": str(log.exercise.section.book_id),
                "section": str(log.exercise.section_id),
                "exercise": str(log.exercise_id),
                "page_number": str(log.exercise.page_number or ""),
                "practiced_on": datetime.date(2026, 4, 24).isoformat(),
                "tempo": "",
                "difficulty": str(PracticeLog.Difficulty.EASY),
                "relaxation_level": str(PracticeLog.RelaxationLevel.RELAXED),
                "notes": "",
            },
            **HTMX_HEADERS,
        )

        assert row_response.status_code == HTTPStatus.OK
        assert edit_response.status_code == HTTPStatus.OK
        assert b"edit-exercise-" in edit_response.content
        assert update_success.status_code == HTTPStatus.OK
        assert log.tempo == 120
        assert update_error.status_code == HTTPStatus.OK
        assert b"This field is required." in update_error.content
