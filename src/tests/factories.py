import datetime

import factory
from factory.django import DjangoModelFactory

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book
        skip_postgeneration_save = True

    title = factory.Faker("sentence", nb_words=3)
    page_count = factory.Faker("random_int", min=50, max=500)

    @factory.post_generation  # type: ignore[misc]
    def authors(self, create: bool, extracted: list[Author] | None, **kwargs: object) -> None:
        if not create:
            return
        if extracted:
            self.authors.add(*extracted)


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section

    book = factory.SubFactory(BookFactory)
    title = factory.LazyAttribute(lambda o: f"Section {o.order}")
    order = factory.Sequence(lambda n: n + 1)


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word")


class ExerciseFactory(DjangoModelFactory):
    class Meta:
        model = Exercise
        skip_postgeneration_save = True

    section = factory.SubFactory(SectionFactory)
    identifier = factory.Sequence(lambda n: str(n + 1))

    @factory.post_generation
    def tags(self, create: bool, extracted: list[Tag] | None, **kwargs: object) -> None:
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)


class PracticeLogFactory(DjangoModelFactory):
    class Meta:
        model = PracticeLog

    exercise = factory.SubFactory(ExerciseFactory)
    practiced_on = factory.LazyFunction(datetime.date.today)
    tempo = factory.Faker("random_int", min=40, max=300)
