from typing import TYPE_CHECKING

import pytest

from tests.factories import AuthorFactory, BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory, TagFactory

if TYPE_CHECKING:
    from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag


@pytest.fixture
def author() -> Author:
    return AuthorFactory(first_name="George", last_name="Stone")


@pytest.fixture
def book(author: Author) -> Book:
    return BookFactory(title="Stick Control", page_count=190, authors=[author])


@pytest.fixture
def section(book: Book) -> Section:
    return SectionFactory(book=book, title="Chapter 1", order=1)


@pytest.fixture
def exercise(section: Section) -> Exercise:
    return ExerciseFactory(section=section, identifier="1")


@pytest.fixture
def tag() -> Tag:
    return TagFactory(name="Paradiddles")


@pytest.fixture
def practice_log(exercise: Exercise) -> PracticeLog:
    return PracticeLogFactory(exercise=exercise, tempo=120)
