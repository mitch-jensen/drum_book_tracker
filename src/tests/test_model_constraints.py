import pytest
from django.db import IntegrityError

from book_tracker.models import Book, Exercise, PracticeLog, Section
from tests.factories import BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory, TagFactory

pytestmark = pytest.mark.django_db


def test_section_order_must_be_unique_per_book(book: Book) -> None:
    SectionFactory(book=book, order=1)

    with pytest.raises(IntegrityError):
        SectionFactory(book=book, order=1)


def test_section_order_can_repeat_across_books(book: Book) -> None:
    other_book = BookFactory()

    SectionFactory(book=book, order=1)
    repeated_order_section = SectionFactory(book=other_book, order=1)

    assert repeated_order_section.book_id == other_book.id


def test_exercise_number_must_be_unique_per_section(section: Section) -> None:
    ExerciseFactory(section=section, exercise_number=1)

    with pytest.raises(IntegrityError):
        ExerciseFactory(section=section, exercise_number=1)


def test_exercise_number_can_repeat_across_sections(book: Book) -> None:
    section_1 = SectionFactory(book=book, order=1)
    section_2 = SectionFactory(book=book, order=2)

    ExerciseFactory(section=section_1, exercise_number=1)
    repeated_number_exercise = ExerciseFactory(section=section_2, exercise_number=1)

    assert repeated_number_exercise.section_id == section_2.id


def test_tag_name_is_globally_unique() -> None:
    TagFactory(name="Paradiddles")

    with pytest.raises(IntegrityError):
        TagFactory(name="Paradiddles")


def test_deleting_book_cascades_to_sections_exercises_and_practice_logs(book: Book) -> None:
    section = SectionFactory(book=book, order=1)
    exercise = ExerciseFactory(section=section, exercise_number=1)
    PracticeLogFactory(exercise=exercise)

    book.delete()

    assert Section.objects.count() == 0
    assert Exercise.objects.count() == 0
    assert PracticeLog.objects.count() == 0
