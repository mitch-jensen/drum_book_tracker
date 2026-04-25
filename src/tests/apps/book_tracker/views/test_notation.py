from http import HTTPStatus  # noqa: INP001
from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from tests.factories import ExerciseFactory

if TYPE_CHECKING:
    from django.test import Client


pytestmark = pytest.mark.django_db


def _create_test_image() -> SimpleUploadedFile:
    """Create a minimal valid PNG image for upload testing."""
    img = Image.new("RGB", (10, 10), color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile("test_notation.png", buffer.read(), content_type="image/png")


class TestExerciseUploadNotation:
    def test_uploads_notation_image(self, client: Client) -> None:
        exercise = ExerciseFactory()
        image = _create_test_image()

        response = client.post(
            reverse("exercise-upload-notation", args=[exercise.pk]),
            {"notation_image": image},
        )

        assert response.status_code == HTTPStatus.FOUND
        exercise.refresh_from_db()
        assert exercise.notation_image

    def test_replaces_existing_image(self, client: Client) -> None:
        exercise = ExerciseFactory()
        image1 = _create_test_image()
        client.post(reverse("exercise-upload-notation", args=[exercise.pk]), {"notation_image": image1})
        exercise.refresh_from_db()
        assert exercise.notation_image

        image2 = _create_test_image()
        response = client.post(
            reverse("exercise-upload-notation", args=[exercise.pk]),
            {"notation_image": image2},
        )

        assert response.status_code == HTTPStatus.FOUND
        exercise.refresh_from_db()
        assert exercise.notation_image

    def test_rejects_get_request(self, client: Client) -> None:
        exercise = ExerciseFactory()
        response = client.get(reverse("exercise-upload-notation", args=[exercise.pk]))
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_redirects_to_detail(self, client: Client) -> None:
        exercise = ExerciseFactory()
        image = _create_test_image()

        response = client.post(
            reverse("exercise-upload-notation", args=[exercise.pk]),
            {"notation_image": image},
        )

        assert response.status_code == HTTPStatus.FOUND
        assert response["Location"] == reverse("exercise-detail", args=[exercise.pk])


class TestExerciseDetailNotation:
    def test_shows_upload_form(self, client: Client) -> None:
        exercise = ExerciseFactory()

        response = client.get(reverse("exercise-detail", args=[exercise.pk]))

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Upload" in content
        assert "Notation Image" in content

    def test_shows_image_when_uploaded(self, client: Client) -> None:
        exercise = ExerciseFactory()
        image = _create_test_image()
        client.post(reverse("exercise-upload-notation", args=[exercise.pk]), {"notation_image": image})

        response = client.get(reverse("exercise-detail", args=[exercise.pk]))

        assert response.status_code == HTTPStatus.OK
        content = response.content.decode()
        assert "Replace" in content
        assert "Notation Image" in content
