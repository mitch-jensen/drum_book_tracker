import pytest  # noqa: INP001
from django.db import IntegrityError

from book_tracker.models import Book, Exercise, PracticeLog, Section
from tests.factories import BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory, TagFactory

pytestmark = pytest.mark.django_db


def test_section_order_must_be_unique_per_book(book: Book) -> None:
    SectionFactory.create(book=book, order=1)

    with pytest.raises(IntegrityError):
        SectionFactory.create(book=book, order=1)


def test_section_order_can_repeat_across_books(book: Book) -> None:
    other_book = BookFactory.create()

    SectionFactory.create(book=book, order=1)
    repeated_order_section = SectionFactory.create(book=other_book, order=1)

    assert repeated_order_section.book_id == other_book.id


def test_exercise_identifier_must_be_unique_per_section(section: Section) -> None:
    ExerciseFactory.create(section=section, identifier="1")

    with pytest.raises(IntegrityError):
        ExerciseFactory.create(section=section, identifier="1")


def test_exercise_identifier_can_repeat_across_sections(book: Book) -> None:
    section_1 = SectionFactory.create(book=book, order=1)
    section_2 = SectionFactory.create(book=book, order=2)

    ExerciseFactory.create(section=section_1, identifier="1")
    repeated_identifier_exercise = ExerciseFactory.create(section=section_2, identifier="1")

    assert repeated_identifier_exercise.section_id == section_2.id


def test_tag_name_is_globally_unique() -> None:
    TagFactory.create(name="Paradiddles")

    with pytest.raises(IntegrityError):
        TagFactory.create(name="Paradiddles")


def test_deleting_book_cascades_to_sections_exercises_and_practice_logs(book: Book) -> None:
    section = SectionFactory.create(book=book, order=1)
    exercise = ExerciseFactory.create(section=section, identifier="1")
    PracticeLogFactory.create(exercise=exercise)

    book.delete()

    assert Section.objects.count() == 0
    assert Exercise.objects.count() == 0
    assert PracticeLog.objects.count() == 0
