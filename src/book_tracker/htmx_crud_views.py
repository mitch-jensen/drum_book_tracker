from __future__ import annotations

import functools
from http import HTTPStatus
from typing import TYPE_CHECKING, NamedTuple

from django.db import transaction
from django.db.models import IntegerField, Max, Prefetch, QuerySet
from django.db.models.functions import Cast
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from book_tracker.bulk_forms import build_form_rows
from book_tracker.forms import (
    BookForm,
    BulkSectionCreateForm,
    ExerciseForm,
    ExerciseTagFilterForm,
    PracticeLogForm,
    SectionForm,
    TagForm,
)
from book_tracker.models import Book, Exercise, PracticeLog, Section, Tag

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.htmx import HtmxHttpRequest

require_DELETE = require_http_methods(["DELETE"])  # noqa: N816


class SectionFormRow(NamedTuple):
    section_title: str


def require_htmx(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(view_func)
    def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not getattr(request, "htmx", False):
            return HttpResponseBadRequest()
        return view_func(request, *args, **kwargs)

    return wrapped


def get_tags() -> QuerySet[Tag]:
    return Tag.objects.order_by("name")


@require_GET
def tag_list(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/tags/list.html",
        {
            "tags": get_tags(),
            "form": TagForm(),
        },
    )


@require_GET
@require_htmx
def tag_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    return render(request, "book_tracker/tags/_row.html", {"tag": tag})


@require_POST
@require_htmx
def tag_create(request: HtmxHttpRequest) -> HttpResponse:
    form = TagForm(request.POST)

    if form.is_valid():
        form.save()
        response = render(
            request,
            "book_tracker/tags/_list.html",
            {
                "tags": get_tags(),
                "form": TagForm(),
            },
        )
        response["HX-Retarget"] = "#tag-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response

    return render(
        request,
        "book_tracker/tags/_create_form.html",
        {"form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def tag_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    form = TagForm(instance=tag)
    return render(request, "book_tracker/tags/_row_form.html", {"tag": tag, "form": form})


@require_POST
@require_htmx
def tag_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    form = TagForm(request.POST, instance=tag)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/tags/_table_body.html",
            {"tags": get_tags()},
        )

    return render(
        request,
        "book_tracker/tags/_row_form.html",
        {"tag": tag, "form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def tag_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    return render(request, "book_tracker/tags/_row_confirm_delete.html", {"tag": tag})


@require_DELETE
@require_htmx
def tag_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    return render(
        request,
        "book_tracker/tags/_table_body.html",
        {"tags": get_tags()},
    )


def get_books() -> QuerySet[Book]:
    return Book.objects.prefetch_related("authors").order_by("title")


@require_GET
def book_list(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/books/list.html",
        {
            "books": get_books(),
            "form": BookForm(),
        },
    )


@require_GET
@require_htmx
def book_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book.objects.prefetch_related("authors"), pk=pk)
    return render(request, "book_tracker/books/_row.html", {"book": book})


@require_POST
@require_htmx
def book_create(request: HtmxHttpRequest) -> HttpResponse:
    form = BookForm(request.POST)

    if form.is_valid():
        form.save()
        response = render(
            request,
            "book_tracker/books/_list.html",
            {
                "books": get_books(),
                "form": BookForm(),
            },
        )
        response["HX-Retarget"] = "#book-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response

    return render(
        request,
        "book_tracker/books/_create_form.html",
        {"form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def book_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book.objects.prefetch_related("authors"), pk=pk)
    form = BookForm(instance=book)
    return render(request, "book_tracker/books/_row_form.html", {"book": book, "form": form})


@require_POST
@require_htmx
def book_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book.objects.prefetch_related("authors"), pk=pk)
    form = BookForm(request.POST, instance=book)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/books/_table_body.html",
            {"books": get_books()},
        )

    return render(
        request,
        "book_tracker/books/_row_form.html",
        {"book": book, "form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def book_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book.objects.prefetch_related("authors"), pk=pk)
    return render(request, "book_tracker/books/_row_confirm_delete.html", {"book": book})


@require_DELETE
@require_htmx
def book_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return render(
        request,
        "book_tracker/books/_table_body.html",
        {"books": get_books()},
    )


def get_sections() -> QuerySet[Section]:
    return Section.objects.select_related("book").order_by("book__title", "order")


def get_section_books() -> QuerySet[Book]:
    return Book.objects.prefetch_related(Prefetch("sections", queryset=Section.objects.order_by("order"))).filter(sections__isnull=False).distinct().order_by("title")


@require_GET
def section_list(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/sections/list.html",
        {
            "sections": get_sections(),
            "section_books": get_section_books(),
            "form": SectionForm(),
        },
    )


@require_GET
@require_htmx
def section_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section.objects.select_related("book"), pk=pk)
    return render(request, "book_tracker/sections/_row.html", {"section": section})


@require_GET
@require_htmx
def section_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section.objects.select_related("book"), pk=pk)
    form = SectionForm(instance=section)
    return render(request, "book_tracker/sections/_row_form.html", {"section": section, "form": form})


@require_POST
@require_htmx
def section_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section.objects.select_related("book"), pk=pk)
    form = SectionForm(request.POST, instance=section)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/sections/_table_body.html",
            {"sections": get_sections(), "section_books": get_section_books()},
        )

    return render(
        request,
        "book_tracker/sections/_row_form.html",
        {"section": section, "form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def section_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section.objects.select_related("book"), pk=pk)
    return render(request, "book_tracker/sections/_row_confirm_delete.html", {"section": section})


@require_DELETE
@require_htmx
def section_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section, pk=pk)
    section.delete()
    return render(
        request,
        "book_tracker/sections/_table_body.html",
        {"sections": get_sections(), "section_books": get_section_books()},
    )


def _section_form_rows_from_post(request: HtmxHttpRequest) -> list[SectionFormRow]:
    return build_form_rows(
        request.POST,
        ("section_title",),
        SectionFormRow,
        SectionFormRow(section_title=""),
    )


def _validate_section_form_rows(rows: list[SectionFormRow]) -> tuple[list[str], list[str]]:
    parsed_rows: list[str] = []
    errors: list[str] = []

    for row_index, row in enumerate(rows, 1):
        title = row.section_title.strip()

        if not title:
            errors.append(f"Section row {row_index}: title is required.")
            continue

        parsed_rows.append(title)

    return parsed_rows, errors


def _render_section_bulk_create(
    request: HtmxHttpRequest,
    form: BulkSectionCreateForm,
    section_rows: list[SectionFormRow],
    section_row_errors: list[str] | None = None,
) -> HttpResponse:
    return render(
        request,
        "book_tracker/sections/bulk_create.html",
        {
            "form": form,
            "section_rows": section_rows,
            "section_row_errors": section_row_errors or [],
        },
    )


def section_bulk_create(request: HtmxHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BulkSectionCreateForm(request.POST)
        section_rows = _section_form_rows_from_post(request)
        section_row_errors: list[str] = []

        if form.is_valid():
            book = form.cleaned_data["book"]
            parsed_rows, section_row_errors = _validate_section_form_rows(section_rows)

            if not section_row_errors:
                next_order = (Section.objects.filter(book=book).order_by("-order").values_list("order", flat=True).first() or 0) + 1
                Section.objects.bulk_create(
                    [Section(book=book, title=title, order=next_order + index) for index, title in enumerate(parsed_rows)],
                )
                return redirect("section-list")

        return _render_section_bulk_create(request, form, section_rows, section_row_errors)

    return _render_section_bulk_create(
        request,
        BulkSectionCreateForm(),
        [SectionFormRow(section_title="")],
    )


@require_GET
@require_htmx
def section_form_row(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/sections/_section_form_row.html",
        {"section_title": ""},
    )


@require_POST
@require_htmx
def section_reorder(request: HtmxHttpRequest) -> HttpResponse:
    section_ids = request.POST.getlist("section")
    sections = list(Section.objects.select_related("book").filter(pk__in=section_ids))

    if len(sections) != len(section_ids):
        return HttpResponseBadRequest()

    sections_by_id = {str(section.pk): section for section in sections}
    ordered_sections = [sections_by_id[section_id] for section_id in section_ids]
    book_ids = {section.book_id for section in ordered_sections}

    if len(book_ids) != 1:
        return HttpResponseBadRequest()

    book_id = next(iter(book_ids))
    book_section_ids = set(Section.objects.filter(book_id=book_id).values_list("pk", flat=True))

    if {section.pk for section in ordered_sections} != book_section_ids:
        return HttpResponseBadRequest()

    max_order = Section.objects.filter(book_id=book_id).aggregate(max_order=Max("order"))["max_order"] or 0

    with transaction.atomic():
        for index, section in enumerate(ordered_sections, 1):
            section.order = max_order + index
            section.save(update_fields=["order"])

        for index, section in enumerate(ordered_sections, 1):
            section.order = index
            section.save(update_fields=["order"])

    return render(
        request,
        "book_tracker/sections/_list.html",
        {
            "sections": get_sections(),
            "section_books": get_section_books(),
        },
    )


def get_exercises() -> QuerySet[Exercise]:
    exercises = Exercise.objects.select_related("section__book").prefetch_related("tags")
    identifiers = exercises.values_list("identifier", flat=True)

    if all(identifier.isdigit() for identifier in identifiers if identifier):
        return exercises.order_by(
            "section__book__title",
            "section__order",
            Cast("identifier", IntegerField()),
        )

    return exercises.order_by(
        "section__book__title",
        "section__order",
        "identifier",
    )


@require_GET
def exercise_list(request: HtmxHttpRequest) -> HttpResponse:
    filter_form = ExerciseTagFilterForm(request.GET or None)
    exercises = get_exercises()

    if filter_form.is_valid() and filter_form.cleaned_data["tags"]:
        exercises = exercises.filter(tags__in=filter_form.cleaned_data["tags"]).distinct()

    return render(
        request,
        "book_tracker/exercises/list.html",
        {
            "exercises": exercises,
            "form": ExerciseForm(),
            "filter_form": filter_form,
        },
    )


@require_GET
@require_htmx
def exercise_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    return render(request, "book_tracker/exercises/_row.html", {"exercise": exercise})


@require_POST
@require_htmx
def exercise_create(request: HtmxHttpRequest) -> HttpResponse:
    form = ExerciseForm(request.POST)

    if form.is_valid():
        form.save()
        response = render(
            request,
            "book_tracker/exercises/_list.html",
            {
                "exercises": get_exercises(),
                "form": ExerciseForm(),
                "filter_form": ExerciseTagFilterForm(),
            },
        )
        response["HX-Retarget"] = "#exercise-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response

    return render(
        request,
        "book_tracker/exercises/_create_form.html",
        {"form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def exercise_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    form = ExerciseForm(instance=exercise)
    return render(request, "book_tracker/exercises/_row_form.html", {"exercise": exercise, "form": form})


@require_POST
@require_htmx
def exercise_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    form = ExerciseForm(request.POST, instance=exercise)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/exercises/_table_body.html",
            {"exercises": get_exercises()},
        )

    return render(
        request,
        "book_tracker/exercises/_row_form.html",
        {"exercise": exercise, "form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def exercise_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    return render(request, "book_tracker/exercises/_row_confirm_delete.html", {"exercise": exercise})


@require_DELETE
@require_htmx
def exercise_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise, pk=pk)
    exercise.delete()
    return render(
        request,
        "book_tracker/exercises/_table_body.html",
        {"exercises": get_exercises()},
    )


def get_logs() -> QuerySet[PracticeLog]:
    return PracticeLog.objects.select_related("exercise__section__book").order_by("-practiced_on", "-pk")


@require_GET
def practice_log_list(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/logs/list.html",
        {
            "logs": get_logs(),
            "form": PracticeLogForm(),
        },
    )


@require_GET
@require_htmx
def practice_log_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog.objects.select_related("exercise__section__book"), pk=pk)
    return render(request, "book_tracker/logs/_row.html", {"log": log})


@require_POST
@require_htmx
def practice_log_create(request: HtmxHttpRequest) -> HttpResponse:
    form = PracticeLogForm(request.POST)

    if form.is_valid():
        form.save()
        response = render(
            request,
            "book_tracker/logs/_list.html",
            {
                "logs": get_logs(),
                "form": PracticeLogForm(),
            },
        )
        response["HX-Retarget"] = "#log-list-container"
        response["HX-Reswap"] = "innerHTML"
        response["HX-Trigger"] = "logCreated"
        return response

    return render(
        request,
        "book_tracker/logs/_create_form.html",
        {"form": form},
        status=HTTPStatus.BAD_REQUEST,
    )


def _log_edit_context(
    log: PracticeLog,
    form: PracticeLogForm,
    book_id: object | None = None,
    section_id: object | None = None,
) -> dict[str, object]:
    current_book_id = book_id or log.exercise.section.book_id
    current_section_id = section_id or log.exercise.section_id
    form.fields["exercise"].widget.attrs["id"] = f"edit-exercise-{log.id}"

    return {
        "log": log,
        "form": form,
        "books": Book.objects.order_by("title"),
        "sections": Section.objects.filter(book_id=current_book_id).order_by("order"),
        "current_book_id": current_book_id,
        "current_section_id": current_section_id,
    }


@require_GET
@require_htmx
def practice_log_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog.objects.select_related("exercise__section__book"), pk=pk)
    form = PracticeLogForm(instance=log)
    return render(request, "book_tracker/logs/_row_form.html", _log_edit_context(log, form))


@require_POST
@require_htmx
def practice_log_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog.objects.select_related("exercise__section__book"), pk=pk)
    form = PracticeLogForm(request.POST, instance=log)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/logs/_table_body.html",
            {"logs": get_logs()},
        )

    return render(
        request,
        "book_tracker/logs/_row_form.html",
        _log_edit_context(
            log,
            form,
            book_id=request.POST.get("book") or None,
            section_id=request.POST.get("section") or None,
        ),
        status=HTTPStatus.BAD_REQUEST,
    )


@require_GET
@require_htmx
def practice_log_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog.objects.select_related("exercise__section__book"), pk=pk)
    return render(request, "book_tracker/logs/_row_confirm_delete.html", {"log": log})


@require_DELETE
@require_htmx
def practice_log_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog, pk=pk)
    log.delete()
    return render(
        request,
        "book_tracker/logs/_table_body.html",
        {"logs": get_logs()},
    )
