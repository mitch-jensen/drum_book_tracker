import datetime
import uuid
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Author(models.Model):
    """Drum book author."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    if TYPE_CHECKING:
        books: RelatedManager[Book]

    def __repr__(self) -> str:
        return f"<Author(id={self.id}, name={self.first_name} {self.last_name})>"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    """Drum book."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    page_count = models.PositiveIntegerField()
    authors = models.ManyToManyField[Author, Author](Author, related_name="books")

    if TYPE_CHECKING:
        sections: RelatedManager[Section]

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        authors: str = ", ".join([str(author) for author in self.authors.all()])
        return f"<Book(id={self.id}, title={self.title}, authors=[{authors}])>"


class Section(models.Model):
    """Drum book section."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sections")
    book_id: uuid.UUID
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    if TYPE_CHECKING:
        exercises: RelatedManager[Exercise]

    class Meta:  # noqa: D106
        constraints = (models.UniqueConstraint(fields=["book", "order"], name="unique_section_order"),)

    def __str__(self) -> str:
        return f"{self.book.title} - {self.title}"

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, title={self.title}, book={self.book.title}, order={self.order})>"


class Tag(models.Model):
    """Drum book tag."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    if TYPE_CHECKING:
        exercises: RelatedManager[Exercise]

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name={self.name})>"

    def __str__(self) -> str:
        return self.name


class Exercise(models.Model):
    """Drum book exercise."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="exercises")
    section_id: uuid.UUID
    title = models.CharField(max_length=255)
    exercise_number = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField[Tag, Tag](Tag, related_name="exercises", blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)

    if TYPE_CHECKING:
        practice_logs: RelatedManager[PracticeLog]

    class Meta:  # noqa: D106
        constraints = (models.UniqueConstraint(fields=["section", "exercise_number"], name="unique_exercise_number"),)

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, title={self.title}, section={self.section.title}, exercise_number={self.exercise_number})>"

    def __str__(self) -> str:
        return f"{self.section.book.title} - {self.title}"


class PracticeLog(models.Model):
    """Drum book practice log."""

    class Difficulty(models.IntegerChoices):
        """Difficulty rating for exercise."""

        NOT_RATED = 0, "Not Rated"
        VERY_EASY = 1, "Very Easy"
        EASY = 2, "Easy"
        MEDIUM = 3, "Medium"
        HARD = 4, "Hard"
        VERY_HARD = 5, "Very Hard"

    class RelaxationLevel(models.IntegerChoices):
        """Relaxation level rating for exercise."""

        NOT_RECORDED = 0, "Not Recorded"
        VERY_TENSE = 1, "Very Tense"
        TENSE = 2, "Tense"
        NEUTRAL = 3, "Neutral"
        RELAXED = 4, "Relaxed"
        VERY_RELAXED = 5, "Very Relaxed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="practice_logs")
    exercise_id: uuid.UUID
    practiced_on = models.DateField(default=datetime.date.today, db_index=True)
    tempo = models.PositiveIntegerField()
    notes = models.TextField(blank=True, default="")
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices, default=Difficulty.NOT_RATED)
    relaxation_level = models.PositiveSmallIntegerField(choices=RelaxationLevel.choices, default=RelaxationLevel.NOT_RECORDED)

    class Meta:  # noqa: D106
        indexes = (models.Index(fields=["exercise", "practiced_on"], name="idx_practice_exercise_date"),)

    def __repr__(self) -> str:
        return f"<PracticeLog(id={self.id}, exercise={self.exercise.title}, practiced_on={self.practiced_on}, tempo={self.tempo})>"

    def __str__(self) -> str:
        return f"{self.exercise.title} - {self.practiced_on} @ {self.tempo} BPM"
