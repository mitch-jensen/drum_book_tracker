from typing import TYPE_CHECKING

import pytest

from tests.factories import AuthorFactory, BookFactory, ExerciseFactory, PracticeLogFactory, SectionFactory, TagFactory

if TYPE_CHECKING:
    from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag


@pytest.fixture
def author() -> Author:
    return AuthorFactory.create(first_name="George", last_name="Stone")  # pyrefly: ignore[bad-return]


@pytest.fixture
def book(author: Author) -> Book:
    return BookFactory.create(title="Stick Control", page_count=190, authors=[author])  # pyrefly: ignore[bad-return]


@pytest.fixture
def section(book: Book) -> Section:
    return SectionFactory.create(book=book, title="Chapter 1", order=1)  # pyrefly: ignore[bad-return]


@pytest.fixture
def exercise(section: Section) -> Exercise:
    return ExerciseFactory.create(section=section, identifier="1")  # pyrefly: ignore[bad-return]


@pytest.fixture
def tag() -> Tag:
    return TagFactory.create(name="Paradiddles")  # pyrefly: ignore[bad-return]


@pytest.fixture
def practice_log(exercise: Exercise) -> PracticeLog:
    return PracticeLogFactory.create(exercise=exercise, tempo=120)  # pyrefly: ignore[bad-return]
