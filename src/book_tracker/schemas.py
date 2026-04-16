import datetime
import uuid
from enum import StrEnum
from typing import Any

from ninja import Schema

from book_tracker.models import PracticeLog


class DifficultyEnum(StrEnum):
    NOT_RATED = "NOT_RATED"
    VERY_EASY = "VERY_EASY"
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


class RelaxationLevelEnum(StrEnum):
    NOT_RECORDED = "NOT_RECORDED"
    VERY_TENSE = "VERY_TENSE"
    TENSE = "TENSE"
    NEUTRAL = "NEUTRAL"
    RELAXED = "RELAXED"
    VERY_RELAXED = "VERY_RELAXED"


DIFFICULTY_TO_INT: dict[str, int] = {m.name: m.value for m in PracticeLog.Difficulty}
DIFFICULTY_FROM_INT: dict[int, str] = {m.value: m.name for m in PracticeLog.Difficulty}
RELAXATION_TO_INT: dict[str, int] = {m.name: m.value for m in PracticeLog.RelaxationLevel}
RELAXATION_FROM_INT: dict[int, str] = {m.value: m.name for m in PracticeLog.RelaxationLevel}


# --- Author ---


class AuthorIn(Schema):
    first_name: str
    last_name: str


class AuthorOut(Schema):
    id: uuid.UUID
    first_name: str
    last_name: str


class AuthorUpdate(Schema):
    first_name: str | None = None
    last_name: str | None = None


# --- Book ---


class BookIn(Schema):
    title: str
    page_count: int
    author_ids: list[uuid.UUID] = []


class BookOut(Schema):
    id: uuid.UUID
    title: str
    page_count: int
    authors: list[AuthorOut]

    @staticmethod
    def resolve_authors(obj: Any) -> list:
        return list(obj.authors.all())


class BookUpdate(Schema):
    title: str | None = None
    page_count: int | None = None
    author_ids: list[uuid.UUID] | None = None


# --- Section ---


class SectionIn(Schema):
    book_id: uuid.UUID
    title: str
    order: int


class SectionOut(Schema):
    id: uuid.UUID
    book_id: uuid.UUID
    title: str
    order: int


class SectionUpdate(Schema):
    title: str | None = None
    order: int | None = None


# --- Tag ---


class TagIn(Schema):
    name: str


class TagOut(Schema):
    id: uuid.UUID
    name: str


class TagUpdate(Schema):
    name: str | None = None


# --- Exercise ---


class ExerciseIn(Schema):
    section_id: uuid.UUID
    title: str
    exercise_number: int
    tag_ids: list[uuid.UUID] = []
    page_number: int | None = None


class ExerciseOut(Schema):
    id: uuid.UUID
    section_id: uuid.UUID
    title: str
    exercise_number: int
    tags: list[TagOut]
    page_number: int | None

    @staticmethod
    def resolve_tags(obj: Any) -> list:
        return list(obj.tags.all())


class ExerciseUpdate(Schema):
    title: str | None = None
    exercise_number: int | None = None
    tag_ids: list[uuid.UUID] | None = None
    page_number: int | None = None


# --- PracticeLog ---


class PracticeLogIn(Schema):
    exercise_id: uuid.UUID
    practiced_on: datetime.date | None = None
    tempo: int
    notes: str = ""
    difficulty: DifficultyEnum = DifficultyEnum.NOT_RATED
    relaxation_level: RelaxationLevelEnum = RelaxationLevelEnum.NOT_RECORDED


class PracticeLogOut(Schema):
    id: uuid.UUID
    exercise_id: uuid.UUID
    practiced_on: datetime.date
    tempo: int
    notes: str
    difficulty: str
    relaxation_level: str

    @staticmethod
    def resolve_difficulty(obj: Any) -> str:
        return PracticeLog.Difficulty(obj.difficulty).name

    @staticmethod
    def resolve_relaxation_level(obj: Any) -> str:
        return PracticeLog.RelaxationLevel(obj.relaxation_level).name


class PracticeLogUpdate(Schema):
    practiced_on: datetime.date | None = None
    tempo: int | None = None
    notes: str | None = None
    difficulty: DifficultyEnum | None = None
    relaxation_level: RelaxationLevelEnum | None = None
