import datetime  # noqa: INP001
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from book_tracker.models import PracticeLog
from tests.factories import BookFactory, ExerciseFactory, SectionFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db

HTMX_HEADERS = {"HTTP_HX-Request": "true"}


class TestExerciseDetailQuickLog:
    def test_quick_log_button_and_form_present(self, client: Client) -> None:
        book = BookFactory.create(page_count=100)
        section = SectionFactory.create(book=book, order=1)
        exercise = ExerciseFactory.create(section=section, identifier="1", page_number=7)

        response = client.get(reverse("exercise-detail", args=[exercise.pk]))
        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Quick Log" in content
        assert "hx-get" in content or "hx-post" in content

    def test_quick_log_creates_practice_log(self, client: Client) -> None:
        book = BookFactory.create(page_count=100)
        section = SectionFactory.create(book=book, order=1)
        exercise = ExerciseFactory.create(section=section, identifier="1", page_number=7)
        url = reverse("exercise-detail", args=[exercise.pk])

        # Simulate quick log form submission (HTMX)
        log_data = {
            "exercise": str(exercise.pk),
            "practiced_on": datetime.date.today().isoformat(),
            "tempo": "120",
            "difficulty": str(PracticeLog.Difficulty.MEDIUM),
            "relaxation_level": str(PracticeLog.RelaxationLevel.NEUTRAL),
            "notes": "Quick log test",
        }
        response = client.post(
            url + "quick-log/",  # This will be the endpoint for the quick log form
            log_data,
            **HTMX_HEADERS,
        )
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED)
        assert PracticeLog.objects.filter(exercise=exercise, tempo=120, notes="Quick log test").exists()
