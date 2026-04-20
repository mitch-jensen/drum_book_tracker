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
    identifier = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    tags = models.ManyToManyField[Tag, Tag](Tag, related_name="exercises", blank=True)
    page_number = models.PositiveIntegerField(null=True, blank=True)

    if TYPE_CHECKING:
        practice_logs: RelatedManager[PracticeLog]

    class Meta:  # noqa: D106
        constraints = (
            models.UniqueConstraint(
                fields=["section", "identifier"],
                name="unique_exercise_identifier",
                condition=~models.Q(identifier=""),
            ),
            models.CheckConstraint(
                condition=~models.Q(identifier="", description=""),
                name="exercise_identifier_or_description_required",
            ),
        )

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, section={self.section.title}, identifier={self.identifier!r})>"

    def __str__(self) -> str:
        label = f"#{self.identifier}" if self.identifier else self.description[:50]
        return f"{self.section.book.title} - {self.section.title} {label}"

    def tempi_practiced(self) -> list[int]:
        """Return a list of tempi practiced for this exercise."""
        return list(self.practice_logs.values_list("tempo", flat=True))

    def minimum_tempo(self) -> int:
        """Return the minimum tempo practiced for this exercise."""
        tempi = self.tempi_practiced()
        return min(tempi) if tempi else 0

    def average_tempo(self) -> float:
        """Return the average tempo practiced for this exercise."""
        tempi = self.tempi_practiced()
        return sum(tempi) / len(tempi) if tempi else 0.0

    def maximum_tempo(self) -> int:
        """Return the maximum tempo practiced for this exercise."""
        tempi = self.tempi_practiced()
        return max(tempi) if tempi else 0

    def most_recent_practice(self) -> datetime.date | None:
        """Return the date of the most recent practice log for this exercise."""
        most_recent_log = self.practice_logs.order_by("-practiced_on").first()
        return most_recent_log.practiced_on if most_recent_log else None

    def practice_count(self) -> int:
        """Return the total number of practice logs for this exercise."""
        return self.practice_logs.count()

    def last_practiced_tempo(self) -> int | None:
        """Return the tempo of the most recent practice log for this exercise."""
        most_recent_log = self.practice_logs.order_by("-practiced_on").first()
        return most_recent_log.tempo if most_recent_log else None

    def last_practiced_difficulty(self) -> int | None:
        """Return the difficulty rating of the most recent practice log for this exercise."""
        most_recent_log = self.practice_logs.order_by("-practiced_on").first()
        return most_recent_log.difficulty if most_recent_log else None

    def last_practiced_relaxation_level(self) -> int | None:
        """Return the relaxation level of the most recent practice log for this exercise."""
        most_recent_log = self.practice_logs.order_by("-practiced_on").first()
        return most_recent_log.relaxation_level if most_recent_log else None

    def average_difficulty(self) -> float:
        """Return the average difficulty across all practice logs, excluding NOT_RATED."""
        result = self.practice_logs.filter(difficulty__gt=0).aggregate(avg=models.Avg("difficulty"))
        return result["avg"] or 0.0

    def average_relaxation_level(self) -> float:
        """Return the average relaxation level across all practice logs, excluding NOT_RECORDED."""
        result = self.practice_logs.filter(relaxation_level__gt=0).aggregate(avg=models.Avg("relaxation_level"))
        return result["avg"] or 0.0

    def first_practiced(self) -> datetime.date | None:
        """Return the date of the earliest practice log for this exercise."""
        earliest_log = self.practice_logs.order_by("practiced_on").first()
        return earliest_log.practiced_on if earliest_log else None


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
        return f"<PracticeLog(id={self.id}, exercise={self.exercise}, practiced_on={self.practiced_on}, tempo={self.tempo})>"

    def __str__(self) -> str:
        return f"{self.exercise} - {self.practiced_on} @ {self.tempo} BPM"
