import uuid
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Author(models.Model):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField[Author, Author](Author, related_name="books")

    if TYPE_CHECKING:
        sections: RelatedManager[Section]

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        authors: str = ", ".join([str(author) for author in self.authors.all()])
        return f"<Book(id={self.id}, title={self.title}, authors=[{authors}])>"


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sections")
    book_id: uuid.UUID
    title = models.CharField(max_length=255)
    order = models.IntegerField()

    if TYPE_CHECKING:
        exercises: RelatedManager[Exercise]

    class Meta:
        constraints = (models.UniqueConstraint(fields=["book", "order"], name="unique_section_order"),)

    def __str__(self) -> str:
        return f"{self.book.title} - {self.title}"

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, title={self.title}, book={self.book.title}, order={self.order})>"


class Tag(models.Model):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="exercises")
    section_id: uuid.UUID
    title = models.CharField(max_length=255)
    exercise_number = models.PositiveSmallIntegerField()
    tags = models.ManyToManyField[Tag, Tag](Tag, related_name="exercises", blank=True)
    page_number = models.IntegerField(null=True, blank=True)

    if TYPE_CHECKING:
        practice_logs: RelatedManager[PracticeLog]

    class Meta:  # noqa: D106
        constraints = (models.UniqueConstraint(fields=["section", "exercise_number"], name="unique_exercise_number"),)

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, title={self.title}, section={self.section.title}, exercise_number={self.exercise_number})>"

    def __str__(self) -> str:
        return f"{self.section.book.title} - {self.title}"


class PracticeLog(models.Model):
    class Difficulty(models.TextChoices):
        NOT_RATED = "", "Not Rated"
        VERY_EASY = "very_easy", "Very Easy"
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"
        VERY_HARD = "very_hard", "Very Hard"

    class RelaxationLevel(models.TextChoices):
        NOT_RECORDED = "", "Not Recorded"
        VERY_TENSE = "very_tense", "Very Tense"
        TENSE = "tense", "Tense"
        NEUTRAL = "neutral", "Neutral"
        RELAXED = "relaxed", "Relaxed"
        VERY_RELAXED = "very_relaxed", "Very Relaxed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="practice_logs")
    exercise_id: uuid.UUID
    practiced_on = models.DateField(auto_now_add=True)
    tempo = models.IntegerField()
    notes = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.NOT_RATED)
    relaxation_level = models.CharField(max_length=12, choices=RelaxationLevel.choices, default=RelaxationLevel.NOT_RECORDED)

    def __repr__(self) -> str:
        return f"<PracticeLog(id={self.id}, exercise={self.exercise.title}, practiced_on={self.practiced_on}, tempo={self.tempo})>"

    def __str__(self) -> str:
        return f"{self.exercise.title} - {self.practiced_on} @ {self.tempo} BPM"
