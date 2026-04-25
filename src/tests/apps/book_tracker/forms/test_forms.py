import datetime  # noqa: INP001

import pytest
from django import forms

from book_tracker.forms import ExerciseForm, PracticeLogForm
from book_tracker.models import Book, Exercise, PracticeLog, Section
from tests.factories import BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory

pytestmark = pytest.mark.django_db


def _require_model_choice_field(field: forms.Field) -> forms.ModelChoiceField:
    assert isinstance(field, forms.ModelChoiceField)
    return field


class TestExerciseForm:
    def test_applies_bootstrap_classes(self) -> None:
        form = ExerciseForm()

        assert form.helper.form_tag is False
        assert form.fields["section"].widget.attrs["class"] == "form-select"
        assert form.fields["tags"].widget.attrs["class"] == "form-select"
        assert form.fields["identifier"].widget.attrs["class"] == "form-control"
        assert form.fields["description"].widget.attrs["class"] == "form-control"
        assert form.fields["page_number"].widget.attrs["class"] == "form-control"


class TestPracticeLogForm:
    def test_defaults_to_empty_dependent_querysets(self) -> None:
        form = PracticeLogForm()

        assert form.helper.form_tag is False
        assert not _require_model_choice_field(form.fields["section"]).queryset.exists()
        assert not _require_model_choice_field(form.fields["exercise"]).queryset.exists()
        assert form.fields["book"].widget.attrs["class"] == "form-select"
        assert form.fields["section"].widget.attrs["class"] == "form-select"
        assert form.fields["exercise"].widget.attrs["class"] == "form-select"
        assert form.fields["page_number"].widget.attrs["class"] == "form-control"
        assert form.fields["tempo"].widget.attrs["class"] == "form-control"

    def test_filters_querysets_from_bound_data(self) -> None:
        book: Book = BookFactory.create(title="Stick Control", page_count=190)
        other_book: Book = BookFactory.create(title="Syncopation", page_count=64)
        section: Section = SectionFactory.create(book=book, title="Chapter 1", order=1)
        later_section: Section = SectionFactory.create(book=book, title="Chapter 2", order=2)
        other_section: Section = SectionFactory.create(book=other_book, title="Chapter 1", order=1)
        matching_exercise: Exercise = ExerciseFactory.create(section=section, identifier="1", page_number=12)
        ExerciseFactory.create(section=section, identifier="2", page_number=8)
        ExerciseFactory.create(section=later_section, identifier="3", page_number=12)
        ExerciseFactory.create(section=other_section, identifier="4", page_number=12)

        form = PracticeLogForm(
            data={
                "book": str(book.pk),
                "section": str(section.pk),
                "page_number": "12",
            },
        )

        assert list(_require_model_choice_field(form.fields["section"]).queryset) == [section, later_section]
        assert list(_require_model_choice_field(form.fields["exercise"]).queryset) == [matching_exercise]

    def test_populates_initials_from_existing_log(self) -> None:
        book: Book = BookFactory.create(title="Stick Control", page_count=190)
        section: Section = SectionFactory.create(book=book, title="Chapter 1", order=1)
        exercise: Exercise = ExerciseFactory.create(section=section, identifier="1", page_number=17)
        second_exercise: Exercise = ExerciseFactory.create(section=section, identifier="2", page_number=19)
        log: PracticeLog = PracticeLogFactory.create(exercise=exercise)

        form = PracticeLogForm(instance=log)

        assert form.fields["book"].initial == book.pk
        assert form.fields["section"].initial == section.pk
        assert form.fields["page_number"].initial == 17
        assert list(_require_model_choice_field(form.fields["exercise"]).queryset) == [exercise, second_exercise]

    def test_uses_bound_data_querysets_when_editing_existing_log(self) -> None:
        book: Book = BookFactory.create(title="Stick Control", page_count=190)
        section_one: Section = SectionFactory.create(book=book, title="Chapter 1", order=1)
        section_two: Section = SectionFactory.create(book=book, title="Chapter 2", order=2)
        original_exercise: Exercise = ExerciseFactory.create(section=section_one, identifier="1", page_number=17)
        target_exercise: Exercise = ExerciseFactory.create(section=section_two, identifier="2", page_number=23)
        ExerciseFactory.create(section=section_one, identifier="3", page_number=23)
        log: PracticeLog = PracticeLogFactory.create(exercise=original_exercise)

        form = PracticeLogForm(
            data={
                "book": str(book.pk),
                "section": str(section_two.pk),
                "page_number": "23",
            },
            instance=log,
        )

        assert list(_require_model_choice_field(form.fields["section"]).queryset) == [section_one, section_two]
        assert list(_require_model_choice_field(form.fields["exercise"]).queryset) == [target_exercise]

    def test_rejects_page_number_above_book_page_count(self) -> None:
        book: Book = BookFactory.create(title="Stick Control", page_count=10)
        section: Section = SectionFactory.create(book=book, title="Chapter 1", order=1)
        exercise: Exercise = ExerciseFactory.create(section=section, identifier="1", page_number=11)

        form = PracticeLogForm(
            data={
                "book": str(book.pk),
                "section": str(section.pk),
                "page_number": "11",
                "exercise": str(exercise.pk),
                "practiced_on": datetime.date(2026, 4, 23).isoformat(),
                "tempo": "120",
                "difficulty": str(PracticeLog.Difficulty.MEDIUM),
                "relaxation_level": str(PracticeLog.RelaxationLevel.NEUTRAL),
                "notes": "",
            },
        )

        assert not form.is_valid()
        assert form.errors["page_number"] == [f"Page number must be between 1 and {book.page_count}."]

    def test_accepts_page_number_within_book_page_count(self) -> None:
        book: Book = BookFactory.create(title="Stick Control", page_count=20)
        section: Section = SectionFactory.create(book=book, title="Chapter 1", order=1)
        exercise: Exercise = ExerciseFactory.create(section=section, identifier="1", page_number=12)

        form = PracticeLogForm(
            data={
                "book": str(book.pk),
                "section": str(section.pk),
                "page_number": "12",
                "exercise": str(exercise.pk),
                "practiced_on": datetime.date(2026, 4, 23).isoformat(),
                "tempo": "120",
                "difficulty": str(PracticeLog.Difficulty.EASY),
                "relaxation_level": str(PracticeLog.RelaxationLevel.RELAXED),
                "notes": "",
            },
        )

        assert form.is_valid()
        assert form.cleaned_data["page_number"] == 12
