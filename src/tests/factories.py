import datetime

import factory
from factory.django import DjangoModelFactory

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag


class AuthorFactory(DjangoModelFactory[Author]):
    class Meta(DjangoModelFactory.Meta):
        model = Author

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class BookFactory(DjangoModelFactory[Book]):
    class Meta(DjangoModelFactory.Meta):
        model = Book
        skip_postgeneration_save = True

    title = factory.Faker("sentence", nb_words=3)
    page_count = factory.Faker("random_int", min=50, max=500)

    @factory.post_generation
    def authors(self: Book, create: bool, extracted: list[Author] | None, **kwargs: object) -> None:
        if not create:
            return
        if extracted:
            self.authors.add(*extracted)


class SectionFactory(DjangoModelFactory[Section]):
    class Meta(DjangoModelFactory.Meta):
        model = Section

    book = factory.SubFactory(BookFactory)
    title = factory.LazyAttribute(lambda o: f"Section {o.order}")
    order = factory.Sequence(lambda n: n + 1)


class TagFactory(DjangoModelFactory[Tag]):
    class Meta(DjangoModelFactory.Meta):
        model = Tag

    name = factory.Faker("word")


class ExerciseFactory(DjangoModelFactory[Exercise]):
    class Meta(DjangoModelFactory.Meta):
        model = Exercise
        skip_postgeneration_save = True

    section = factory.SubFactory(SectionFactory)
    identifier = factory.Sequence(lambda n: str(n + 1))

    @factory.post_generation
    def tags(self: Exercise, create: bool, extracted: list[Tag] | None, **kwargs: object) -> None:
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)


class PracticeLogFactory(DjangoModelFactory[PracticeLog]):
    class Meta(DjangoModelFactory.Meta):
        model = PracticeLog

    exercise = factory.SubFactory(ExerciseFactory)
    practiced_on = factory.LazyFunction(datetime.date.today)
    tempo = factory.Faker("random_int", min=40, max=300)
