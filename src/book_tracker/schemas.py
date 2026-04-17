import uuid  # noqa: TC003

from ninja import Field, ModelSchema

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag


class AuthorIn(ModelSchema):
    class Meta:  # noqa: D106
        model = Author
        fields = ("first_name", "last_name")


class AuthorOut(ModelSchema):
    class Meta:  # noqa: D106
        model = Author
        fields = ("id", "first_name", "last_name")


class AuthorUpdate(ModelSchema):
    class Meta:  # noqa: D106
        model = Author
        fields = ("first_name", "last_name")
        fields_optional = "__all__"


class BookIn(ModelSchema):
    author_ids: list[uuid.UUID] = []  # noqa: RUF012

    class Meta:  # noqa: D106
        model = Book
        fields = ("title", "page_count")


class BookOut(ModelSchema):
    authors: list[AuthorOut]

    class Meta:  # noqa: D106
        model = Book
        fields = ("id", "title", "page_count")

    @staticmethod
    def resolve_authors(obj: Book) -> list[Author]:  # noqa: D102
        return list(obj.authors.all())


class BookUpdate(ModelSchema):
    author_ids: list[uuid.UUID] | None = None

    class Meta:  # noqa: D106
        model = Book
        fields = ("title", "page_count")
        fields_optional = "__all__"


class SectionIn(ModelSchema):
    book_id: uuid.UUID

    class Meta:  # noqa: D106
        model = Section
        fields = ("title", "order")


class SectionOut(ModelSchema):
    book_id: uuid.UUID

    class Meta:  # noqa: D106
        model = Section
        fields = ("id", "title", "order")


class SectionUpdate(ModelSchema):
    class Meta:  # noqa: D106
        model = Section
        fields = ("title", "order")
        fields_optional = "__all__"


class TagIn(ModelSchema):
    class Meta:  # noqa: D106
        model = Tag
        fields = ("name",)


class TagOut(ModelSchema):
    class Meta:  # noqa: D106
        model = Tag
        fields = ("id", "name")


class TagUpdate(ModelSchema):
    class Meta:  # noqa: D106
        model = Tag
        fields = ("name",)
        fields_optional = "__all__"


class ExerciseIn(ModelSchema):
    section_id: uuid.UUID
    tag_ids: list[uuid.UUID] = Field(default_factory=list)

    class Meta:  # noqa: D106
        model = Exercise
        fields = ("title", "exercise_number", "page_number")


class ExerciseOut(ModelSchema):
    section_id: uuid.UUID
    tags: list[TagOut]

    class Meta:  # noqa: D106
        model = Exercise
        fields = ("id", "title", "exercise_number", "page_number")

    @staticmethod
    def resolve_tags(obj: Exercise) -> list[Tag]:  # noqa: D102
        return list(obj.tags.all())


class ExerciseUpdate(ModelSchema):
    tag_ids: list[uuid.UUID] | None = None

    class Meta:  # noqa: D106
        model = Exercise
        fields = ("title", "exercise_number", "page_number")
        fields_optional = "__all__"


class PracticeLogIn(ModelSchema):
    exercise_id: uuid.UUID

    class Meta:  # noqa: D106
        model = PracticeLog
        fields = ("practiced_on", "tempo", "notes", "difficulty", "relaxation_level")
        fields_optional = ("practiced_on", "notes", "difficulty", "relaxation_level")


class PracticeLogOut(ModelSchema):
    exercise_id: uuid.UUID

    class Meta:  # noqa: D106
        model = PracticeLog
        fields = ("id", "practiced_on", "tempo", "notes", "difficulty", "relaxation_level")


class PracticeLogUpdate(ModelSchema):
    class Meta:  # noqa: D106
        model = PracticeLog
        fields = ("practiced_on", "tempo", "notes", "difficulty", "relaxation_level")
        fields_optional = "__all__"
