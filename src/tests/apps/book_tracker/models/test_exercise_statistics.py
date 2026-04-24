import datetime

import pytest

from book_tracker.models import PracticeLog
from tests.factories import ExerciseFactory, PracticeLogFactory

pytestmark = pytest.mark.django_db


class TestExerciseStatistics:
    def test_returns_defaults_when_no_practice_logs(self) -> None:
        exercise = ExerciseFactory()

        assert exercise.tempi_practiced() == []
        assert exercise.minimum_tempo() == 0
        assert exercise.average_tempo() == 0.0
        assert exercise.maximum_tempo() == 0
        assert exercise.most_recent_practice() is None
        assert exercise.practice_count() == 0
        assert exercise.last_practiced_tempo() is None
        assert exercise.last_practiced_difficulty() is None
        assert exercise.last_practiced_relaxation_level() is None
        assert exercise.average_difficulty() == 0.0
        assert exercise.average_relaxation_level() == 0.0
        assert exercise.first_practiced() is None

    def test_calculates_statistics_from_practice_logs(self) -> None:
        exercise = ExerciseFactory()
        older = datetime.date(2026, 4, 20)
        newer = datetime.date(2026, 4, 23)

        PracticeLogFactory(
            exercise=exercise,
            practiced_on=older,
            tempo=80,
            difficulty=PracticeLog.Difficulty.NOT_RATED,
            relaxation_level=PracticeLog.RelaxationLevel.NOT_RECORDED,
        )
        PracticeLogFactory(
            exercise=exercise,
            practiced_on=newer,
            tempo=100,
            difficulty=PracticeLog.Difficulty.HARD,
            relaxation_level=PracticeLog.RelaxationLevel.RELAXED,
        )

        assert exercise.tempi_practiced() == [80, 100]
        assert exercise.minimum_tempo() == 80
        assert exercise.average_tempo() == 90.0
        assert exercise.maximum_tempo() == 100
        assert exercise.most_recent_practice() == newer
        assert exercise.practice_count() == 2
        assert exercise.last_practiced_tempo() == 100
        assert exercise.last_practiced_difficulty() == PracticeLog.Difficulty.HARD
        assert exercise.last_practiced_relaxation_level() == PracticeLog.RelaxationLevel.RELAXED
        assert exercise.average_difficulty() == 4.0
        assert exercise.average_relaxation_level() == 4.0
        assert exercise.first_practiced() == older
