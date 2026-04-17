import datetime

import pytest

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag

pytestmark = pytest.mark.django_db


def test_create_author(author: Author) -> None:
    assert author.first_name == "George"
    assert author.last_name == "Stone"
    assert str(author) == "George Stone"
    assert "George Stone" in repr(author)


def test_create_book(book: Book, author: Author) -> None:
    assert book.title == "Stick Control"
    assert book.page_count == 190
    assert str(book) == "Stick Control"
    assert list(book.authors.all()) == [author]
    assert list(author.books.all()) == [book]


def test_create_section(section: Section, book: Book) -> None:
    assert section.title == "Chapter 1"
    assert section.order == 1
    assert section.book_id == book.id
    assert str(section) == "Stick Control - Chapter 1"
    assert "order=1" in repr(section)


def test_create_exercise(exercise: Exercise, section: Section) -> None:
    assert exercise.title == "Exercise 1"
    assert exercise.exercise_number == 1
    assert exercise.page_number is None
    assert exercise.section_id == section.id
    assert str(exercise) == "Stick Control - Exercise 1"
    assert "exercise_number=1" in repr(exercise)


def test_create_tag(tag: Tag) -> None:
    assert tag.name == "Paradiddles"
    assert str(tag) == "Paradiddles"
    assert "Paradiddles" in repr(tag)
    assert Tag.objects.count() == 1


def test_create_practice_log_defaults(practice_log: PracticeLog, exercise: Exercise) -> None:
    assert practice_log.exercise_id == exercise.id
    assert practice_log.tempo == 120
    assert practice_log.practiced_on == datetime.date.today()
    assert practice_log.notes == ""
    assert practice_log.difficulty == PracticeLog.Difficulty.NOT_RATED
    assert practice_log.relaxation_level == PracticeLog.RelaxationLevel.NOT_RECORDED
    assert str(practice_log).endswith("@ 120 BPM")
    assert "tempo=120" in repr(practice_log)


def test_model_meta_has_expected_constraints_and_indexes() -> None:
    section_constraint_names = {constraint.name for constraint in Section._meta.constraints}
    exercise_constraint_names = {constraint.name for constraint in Exercise._meta.constraints}
    practice_log_index_names = {index.name for index in PracticeLog._meta.indexes}

    assert "unique_section_order" in section_constraint_names
    assert "unique_exercise_number" in exercise_constraint_names
    assert "idx_practice_exercise_date" in practice_log_index_names
