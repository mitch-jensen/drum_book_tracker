from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from tests.factories import ExerciseFactory, TagFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


class TestExerciseListTagFiltering:
    def test_filters_by_single_tag(self, client: Client) -> None:
        groove = TagFactory(name="groove")
        rudiment = TagFactory(name="rudiment")

        matching = ExerciseFactory(description="Groove exercise")
        matching.tags.add(groove)

        non_matching = ExerciseFactory(description="Rudiment exercise")
        non_matching.tags.add(rudiment)

        response = client.get(reverse("exercise-list"), {"tags": [str(groove.id)]})

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Groove exercise" in content
        assert "Rudiment exercise" not in content

    def test_filters_by_multiple_tags(self, client: Client) -> None:
        groove = TagFactory(name="groove")
        rudiment = TagFactory(name="rudiment")
        linear = TagFactory(name="linear")

        groove_exercise = ExerciseFactory(description="Groove exercise")
        groove_exercise.tags.add(groove)

        rudiment_exercise = ExerciseFactory(description="Rudiment exercise")
        rudiment_exercise.tags.add(rudiment)

        other_exercise = ExerciseFactory(description="Linear exercise")
        other_exercise.tags.add(linear)

        response = client.get(reverse("exercise-list"), {"tags": [str(groove.id), str(rudiment.id)]})

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Groove exercise" in content
        assert "Rudiment exercise" in content
        assert "Linear exercise" not in content
