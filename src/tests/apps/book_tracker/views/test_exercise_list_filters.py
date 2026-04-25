from http import HTTPStatus  # noqa: INP001
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from tests.factories import ExerciseFactory, TagFactory

if TYPE_CHECKING:
    from django.test import Client


pytestmark = pytest.mark.django_db


class TestExerciseListTagFiltering:
    def test_filters_by_single_tag(self, client: Client) -> None:
        groove = TagFactory.create(name="groove")
        rudiment = TagFactory.create(name="rudiment")

        matching = ExerciseFactory.create(description="Groove exercise")
        matching.tags.add(groove)

        non_matching = ExerciseFactory.create(description="Rudiment exercise")
        non_matching.tags.add(rudiment)

        response = client.get(reverse("exercise-list"), {"tags": [str(groove.id)]})

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Groove exercise" in content
        assert "Rudiment exercise" not in content

    def test_filters_by_multiple_tags(self, client: Client) -> None:
        groove = TagFactory.create(name="groove")
        rudiment = TagFactory.create(name="rudiment")
        linear = TagFactory.create(name="linear")

        groove_exercise = ExerciseFactory.create(description="Groove exercise")
        groove_exercise.tags.add(groove)

        rudiment_exercise = ExerciseFactory.create(description="Rudiment exercise")
        rudiment_exercise.tags.add(rudiment)

        other_exercise = ExerciseFactory.create(description="Linear exercise")
        other_exercise.tags.add(linear)

        response = client.get(reverse("exercise-list"), {"tags": [str(groove.id), str(rudiment.id)]})

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Groove exercise" in content
        assert "Rudiment exercise" in content
        assert "Linear exercise" not in content
