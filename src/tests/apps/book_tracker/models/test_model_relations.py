import datetime  # noqa: INP001
from typing import cast

import pytest

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag
from tests.factories import AuthorFactory, BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory, TagFactory

pytestmark = pytest.mark.django_db


def test_book_with_multiple_authors() -> None:
    authors = AuthorFactory.create_batch(3)
    book = cast("Book", BookFactory(authors=authors))

    assert book.authors.count() == 3
    for author in authors:
        assert book in author.books.all()


def test_author_with_multiple_books() -> None:
    author = cast("Author", AuthorFactory())
    books = BookFactory.create_batch(3, authors=[author])

    assert author.books.count() == 3
    for book in books:
        assert author in book.authors.all()


def test_book_repr_includes_all_authors() -> None:
    authors = [
        cast("Author", AuthorFactory(first_name="George", last_name="Stone")),
        cast("Author", AuthorFactory(first_name="Ted", last_name="Reed")),
    ]
    book = cast("Book", BookFactory(title="Duet Book", authors=authors))

    book_repr = repr(book)
    assert "George Stone" in book_repr
    assert "Ted Reed" in book_repr


def test_book_with_multiple_sections() -> None:
    book = cast("Book", BookFactory())
    sections = [cast("Section", SectionFactory(book=book, order=i)) for i in range(1, 5)]

    assert book.sections.count() == 4
    assert list(book.sections.order_by("order")) == sections


def test_section_with_multiple_exercises() -> None:
    section = cast("Section", SectionFactory())
    exercises = [cast("Exercise", ExerciseFactory(section=section, identifier=str(i))) for i in range(1, 6)]

    assert section.exercises.count() == 5
    assert list(section.exercises.order_by("identifier")) == exercises


def test_exercise_with_multiple_tags() -> None:
    tags = TagFactory.create_batch(3)
    exercise = cast("Exercise", ExerciseFactory(tags=tags))

    assert exercise.tags.count() == 3
    for tag in tags:
        assert exercise in tag.exercises.all()


def test_tag_shared_across_exercises() -> None:
    tag = cast("Tag", TagFactory(name="Paradiddles"))
    exercises = [cast("Exercise", ExerciseFactory(tags=[tag])) for _ in range(4)]

    assert tag.exercises.count() == 4
    for exercise in exercises:
        assert tag in exercise.tags.all()


def test_practice_logs_across_full_object_graph() -> None:
    """Multiple practice logs across exercises in different sections of different books."""
    author = cast("Author", AuthorFactory())
    books = BookFactory.create_batch(2, authors=[author])
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    all_logs: list[PracticeLog] = []
    for book in books:
        for section_order in range(1, 3):
            section = cast("Section", SectionFactory(book=book, order=section_order))
            for exercise_num in range(1, 3):
                exercise = cast("Exercise", ExerciseFactory(section=section, identifier=str(exercise_num)))
                all_logs.append(cast("PracticeLog", PracticeLogFactory(exercise=exercise, practiced_on=yesterday, tempo=80)))
                all_logs.append(cast("PracticeLog", PracticeLogFactory(exercise=exercise, practiced_on=today, tempo=100)))

    assert PracticeLog.objects.count() == 16  # 2 books * 2 sections * 2 exercises * 2 logs
    assert Exercise.objects.count() == 8
    assert Section.objects.count() == 4
    assert Book.objects.count() == 2

    for book in books:
        book_logs = PracticeLog.objects.filter(exercise__section__book=book)
        assert book_logs.count() == 8


def test_practice_logs_filter_by_date_range() -> None:
    exercise = cast("Exercise", ExerciseFactory())
    today = datetime.date.today()

    dates = [today - datetime.timedelta(days=i) for i in range(7)]
    for d in dates:
        PracticeLogFactory(exercise=exercise, practiced_on=d)

    last_3_days = PracticeLog.objects.filter(practiced_on__gte=today - datetime.timedelta(days=2))
    assert last_3_days.count() == 3


def test_practice_log_with_all_fields_set() -> None:
    log = cast(
        "PracticeLog",
        PracticeLogFactory(
            tempo=140,
            notes="Felt good at this tempo",
            difficulty=PracticeLog.Difficulty.MEDIUM,
            relaxation_level=PracticeLog.RelaxationLevel.RELAXED,
        ),
    )

    log.refresh_from_db()
    assert log.tempo == 140
    assert log.notes == "Felt good at this tempo"
    assert log.difficulty == PracticeLog.Difficulty.MEDIUM
    assert log.relaxation_level == PracticeLog.RelaxationLevel.RELAXED


def test_exercise_with_page_number() -> None:
    exercise = cast("Exercise", ExerciseFactory(page_number=42))

    exercise.refresh_from_db()
    assert exercise.page_number == 42


def test_deleting_section_cascades_to_exercises_and_logs() -> None:
    section = cast("Section", SectionFactory())
    exercises = [cast("Exercise", ExerciseFactory(section=section, identifier=str(i))) for i in range(1, 4)]
    for ex in exercises:
        PracticeLogFactory.create_batch(2, exercise=ex)

    assert PracticeLog.objects.count() == 6
    assert Exercise.objects.count() == 3

    section.delete()

    assert Exercise.objects.count() == 0
    assert PracticeLog.objects.count() == 0


def test_deleting_exercise_cascades_to_practice_logs() -> None:
    exercise = cast("Exercise", ExerciseFactory())
    PracticeLogFactory.create_batch(5, exercise=exercise)

    assert PracticeLog.objects.count() == 5

    exercise.delete()

    assert PracticeLog.objects.count() == 0
