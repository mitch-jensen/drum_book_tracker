from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.title
    
    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"
    
class Section(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'order'], name='unique_section_order')
        ]

    def __str__(self) -> str:
        return f'{self.book.title} - {self.title}'
    
    def __repr__(self):
        return f"<Section(id={self.id}, title={self.title}, book={self.book.title}, order={self.order})>"

    
class Exercise(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=255)
    exercise_number = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['section', 'exercise_number'], name='unique_exercise_number')
        ]

    def __repr__(self):
        return f"<Exercise(id={self.id}, title={self.title}, section={self.section.title}, exercise_number={self.exercise_number})>"

    def __str__(self):
        return f'{self.section.book.title} - {self.title}'


class PracticeLog(models.Model):
    class Difficulty(models.TextChoices):
        NOT_RATED = '', 'Not Rated'
        VERY_EASY = 'very_easy', 'Very Easy'
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'
        VERY_HARD = 'very_hard', 'Very Hard'

    class RelaxationLevel(models.TextChoices):
        NOT_RECORDED = '', 'Not Recorded'
        VERY_TENSE = 'very_tense', 'Very Tense'
        TENSE = 'tense', 'Tense'
        NEUTRAL = 'neutral', 'Neutral'
        RELAXED = 'relaxed', 'Relaxed'
        VERY_RELAXED = 'very_relaxed', 'Very Relaxed'

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='practice_logs')
    practiced_on = models.DateField(auto_now_add=True)
    tempo = models.IntegerField()
    notes = models.TextField(blank=True)
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.NOT_RATED
    )
    relaxation_level = models.CharField(
        max_length=12,
        choices=RelaxationLevel.choices,
        default=RelaxationLevel.NOT_RECORDED
    )

    def __repr__(self):
        return f"<PracticeLog(id={self.id}, exercise={self.exercise.title}, practiced_on={self.practiced_on}, tempo={self.tempo})>"

    def __str__(self):
        return f'{self.exercise.title} - {self.practiced_on} @ {self.tempo} BPM'
