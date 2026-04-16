import datetime
import uuid

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import aget_object_or_404
from ninja import NinjaAPI, Router
from ninja.pagination import LimitOffsetPagination, paginate

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section, Tag
from book_tracker.schemas import (
    AuthorIn,
    AuthorOut,
    AuthorUpdate,
    BookIn,
    BookOut,
    BookUpdate,
    ExerciseIn,
    ExerciseOut,
    ExerciseUpdate,
    PracticeLogIn,
    PracticeLogOut,
    PracticeLogUpdate,
    SectionIn,
    SectionOut,
    SectionUpdate,
    TagIn,
    TagOut,
    TagUpdate,
)

api = NinjaAPI(
    title="Drum Book Tracker API",
    version="1.0.0",
    description="API for tracking drumming practice across exercise books.",
)


@api.exception_handler(IntegrityError)
def integrity_error(request: HttpRequest, exc: IntegrityError) -> HttpResponse:
    return api.create_response(request, {"detail": "Conflict: a unique constraint was violated."}, status=409)


# ---------------------------------------------------------------------------
# Authors
# ---------------------------------------------------------------------------

authors_router = Router(tags=["Authors"])


@authors_router.get("/", response=list[AuthorOut])
@paginate(LimitOffsetPagination)
async def list_authors(request: HttpRequest) -> object:
    return Author.objects.order_by("last_name", "first_name")


@authors_router.get("/{author_id}", response=AuthorOut)
async def get_author(request: HttpRequest, author_id: uuid.UUID) -> Author:
    return await aget_object_or_404(Author, pk=author_id)


@authors_router.post("/", response={201: AuthorOut})
async def create_author(request: HttpRequest, payload: AuthorIn) -> tuple[int, Author]:
    author = await Author.objects.acreate(**payload.model_dump())
    return 201, author


@authors_router.patch("/{author_id}", response=AuthorOut)
async def update_author(request: HttpRequest, author_id: uuid.UUID, payload: AuthorUpdate) -> Author:
    author = await aget_object_or_404(Author, pk=author_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, attr, value)
    await author.asave()
    return author


@authors_router.delete("/{author_id}", response={204: None})
async def delete_author(request: HttpRequest, author_id: uuid.UUID) -> tuple[int, None]:
    author = await aget_object_or_404(Author, pk=author_id)
    await author.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Books
# ---------------------------------------------------------------------------

books_router = Router(tags=["Books"])


@books_router.get("/", response=list[BookOut])
@paginate(LimitOffsetPagination)
async def list_books(request: HttpRequest) -> object:
    return Book.objects.prefetch_related("authors").order_by("title")


@books_router.get("/{book_id}", response=BookOut)
async def get_book(request: HttpRequest, book_id: uuid.UUID) -> Book:
    return await aget_object_or_404(Book.objects.prefetch_related("authors"), pk=book_id)


@books_router.post("/", response={201: BookOut})
async def create_book(request: HttpRequest, payload: BookIn) -> tuple[int, Book]:
    data = payload.model_dump()
    author_ids = data.pop("author_ids")
    book = await Book.objects.acreate(**data)
    if author_ids:
        await book.authors.aset(author_ids)
    return 201, await Book.objects.prefetch_related("authors").aget(pk=book.pk)


@books_router.patch("/{book_id}", response=BookOut)
async def update_book(request: HttpRequest, book_id: uuid.UUID, payload: BookUpdate) -> Book:
    book = await aget_object_or_404(Book, pk=book_id)
    data = payload.model_dump(exclude_unset=True)
    author_ids = data.pop("author_ids", None)
    for attr, value in data.items():
        setattr(book, attr, value)
    await book.asave()
    if author_ids is not None:
        await book.authors.aset(author_ids)
    return await Book.objects.prefetch_related("authors").aget(pk=book_id)


@books_router.delete("/{book_id}", response={204: None})
async def delete_book(request: HttpRequest, book_id: uuid.UUID) -> tuple[int, None]:
    book = await aget_object_or_404(Book, pk=book_id)
    await book.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

sections_router = Router(tags=["Sections"])


@sections_router.get("/", response=list[SectionOut])
@paginate(LimitOffsetPagination)
async def list_sections(request: HttpRequest, book_id: uuid.UUID | None = None) -> object:
    qs = Section.objects.order_by("order")
    if book_id:
        qs = qs.filter(book_id=book_id)
    return qs


@sections_router.get("/{section_id}", response=SectionOut)
async def get_section(request: HttpRequest, section_id: uuid.UUID) -> Section:
    return await aget_object_or_404(Section, pk=section_id)


@sections_router.post("/", response={201: SectionOut})
async def create_section(request: HttpRequest, payload: SectionIn) -> tuple[int, Section]:
    section = await Section.objects.acreate(**payload.model_dump())
    return 201, section


@sections_router.patch("/{section_id}", response=SectionOut)
async def update_section(request: HttpRequest, section_id: uuid.UUID, payload: SectionUpdate) -> Section:
    section = await aget_object_or_404(Section, pk=section_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, attr, value)
    await section.asave()
    return section


@sections_router.delete("/{section_id}", response={204: None})
async def delete_section(request: HttpRequest, section_id: uuid.UUID) -> tuple[int, None]:
    section = await aget_object_or_404(Section, pk=section_id)
    await section.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

tags_router = Router(tags=["Tags"])


@tags_router.get("/", response=list[TagOut])
@paginate(LimitOffsetPagination)
async def list_tags(request: HttpRequest) -> object:
    return Tag.objects.order_by("name")


@tags_router.get("/{tag_id}", response=TagOut)
async def get_tag(request: HttpRequest, tag_id: uuid.UUID) -> Tag:
    return await aget_object_or_404(Tag, pk=tag_id)


@tags_router.post("/", response={201: TagOut})
async def create_tag(request: HttpRequest, payload: TagIn) -> tuple[int, Tag]:
    tag = await Tag.objects.acreate(**payload.model_dump())
    return 201, tag


@tags_router.patch("/{tag_id}", response=TagOut)
async def update_tag(request: HttpRequest, tag_id: uuid.UUID, payload: TagUpdate) -> Tag:
    tag = await aget_object_or_404(Tag, pk=tag_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(tag, attr, value)
    await tag.asave()
    return tag


@tags_router.delete("/{tag_id}", response={204: None})
async def delete_tag(request: HttpRequest, tag_id: uuid.UUID) -> tuple[int, None]:
    tag = await aget_object_or_404(Tag, pk=tag_id)
    await tag.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------

exercises_router = Router(tags=["Exercises"])


@exercises_router.get("/", response=list[ExerciseOut])
@paginate(LimitOffsetPagination)
async def list_exercises(request: HttpRequest, section_id: uuid.UUID | None = None) -> object:
    qs = Exercise.objects.prefetch_related("tags").order_by("exercise_number")
    if section_id:
        qs = qs.filter(section_id=section_id)
    return qs


@exercises_router.get("/{exercise_id}", response=ExerciseOut)
async def get_exercise(request: HttpRequest, exercise_id: uuid.UUID) -> Exercise:
    return await aget_object_or_404(Exercise.objects.prefetch_related("tags"), pk=exercise_id)


@exercises_router.post("/", response={201: ExerciseOut})
async def create_exercise(request: HttpRequest, payload: ExerciseIn) -> tuple[int, Exercise]:
    data = payload.model_dump()
    tag_ids = data.pop("tag_ids")
    exercise = await Exercise.objects.acreate(**data)
    if tag_ids:
        await exercise.tags.aset(tag_ids)
    return 201, await Exercise.objects.prefetch_related("tags").aget(pk=exercise.pk)


@exercises_router.patch("/{exercise_id}", response=ExerciseOut)
async def update_exercise(request: HttpRequest, exercise_id: uuid.UUID, payload: ExerciseUpdate) -> Exercise:
    exercise = await aget_object_or_404(Exercise, pk=exercise_id)
    data = payload.model_dump(exclude_unset=True)
    tag_ids = data.pop("tag_ids", None)
    for attr, value in data.items():
        setattr(exercise, attr, value)
    await exercise.asave()
    if tag_ids is not None:
        await exercise.tags.aset(tag_ids)
    return await Exercise.objects.prefetch_related("tags").aget(pk=exercise_id)


@exercises_router.delete("/{exercise_id}", response={204: None})
async def delete_exercise(request: HttpRequest, exercise_id: uuid.UUID) -> tuple[int, None]:
    exercise = await aget_object_or_404(Exercise, pk=exercise_id)
    await exercise.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Practice Logs
# ---------------------------------------------------------------------------

practice_logs_router = Router(tags=["Practice Logs"])


@practice_logs_router.get("/", response=list[PracticeLogOut])
@paginate(LimitOffsetPagination)
async def list_practice_logs(
    request: HttpRequest,
    exercise_id: uuid.UUID | None = None,
    practiced_on_from: datetime.date | None = None,
    practiced_on_to: datetime.date | None = None,
) -> object:
    qs = PracticeLog.objects.order_by("-practiced_on")
    if exercise_id:
        qs = qs.filter(exercise_id=exercise_id)
    if practiced_on_from:
        qs = qs.filter(practiced_on__gte=practiced_on_from)
    if practiced_on_to:
        qs = qs.filter(practiced_on__lte=practiced_on_to)
    return qs


@practice_logs_router.get("/{practice_log_id}", response=PracticeLogOut)
async def get_practice_log(request: HttpRequest, practice_log_id: uuid.UUID) -> PracticeLog:
    return await aget_object_or_404(PracticeLog, pk=practice_log_id)


@practice_logs_router.post("/", response={201: PracticeLogOut})
async def create_practice_log(request: HttpRequest, payload: PracticeLogIn) -> tuple[int, PracticeLog]:
    data = payload.model_dump(exclude_unset=True)
    log = await PracticeLog.objects.acreate(**data)
    return 201, log


@practice_logs_router.patch("/{practice_log_id}", response=PracticeLogOut)
async def update_practice_log(request: HttpRequest, practice_log_id: uuid.UUID, payload: PracticeLogUpdate) -> PracticeLog:
    log = await aget_object_or_404(PracticeLog, pk=practice_log_id)
    for attr, value in payload.model_dump(exclude_unset=True).items():
        setattr(log, attr, value)
    await log.asave()
    return log


@practice_logs_router.delete("/{practice_log_id}", response={204: None})
async def delete_practice_log(request: HttpRequest, practice_log_id: uuid.UUID) -> tuple[int, None]:
    log = await aget_object_or_404(PracticeLog, pk=practice_log_id)
    await log.adelete()
    return 204, None


# ---------------------------------------------------------------------------
# Register routers (kebab-case path segments per API standards)
# ---------------------------------------------------------------------------

api.add_router("/authors", authors_router)
api.add_router("/books", books_router)
api.add_router("/sections", sections_router)
api.add_router("/tags", tags_router)
api.add_router("/exercises", exercises_router)
api.add_router("/practice-logs", practice_logs_router)
