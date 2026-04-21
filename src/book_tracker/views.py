from typing import TYPE_CHECKING

from django.db.models import Avg, Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from book_tracker.forms import (
    AuthorForm,
    BookForm,
    BulkExerciseCreateForm,
    ExerciseForm,
    NotationUploadForm,
    PracticeLogForm,
    SectionForm,
)
from book_tracker.models import Author, Book, Exercise, PracticeLog, Section
from core.htmx import require_htmx

if TYPE_CHECKING:
    from django.http import HttpResponse

    from core.htmx import HtmxHttpRequest


# --- Author views ---


@require_GET
def author_list(request: HtmxHttpRequest) -> HttpResponse:
    authors = Author.objects.order_by("last_name", "first_name")
    form = AuthorForm()
    return render(request, "book_tracker/authors.html", {"authors": authors, "form": form})


@require_POST
@require_htmx
def author_create(request: HtmxHttpRequest) -> HttpResponse:
    form = AuthorForm(request.POST)
    if form.is_valid():
        form.save()
        authors = Author.objects.order_by("last_name", "first_name")
        response = render(
            request,
            "book_tracker/authors.html#author-list",
            {"authors": authors, "form": AuthorForm()},
        )
        response["HX-Retarget"] = "#author-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response
    return render(request, "book_tracker/authors.html#author-form", {"form": form})


@require_GET
@require_htmx
def author_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    return render(request, "book_tracker/authors.html#author-row", {"author": author})


@require_GET
@require_htmx
def author_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(instance=author)
    return render(request, "book_tracker/author_edit_row.html", {"author": author, "form": form})


@require_POST
@require_htmx
def author_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(request.POST, instance=author)
    if form.is_valid():
        form.save()
        return render(request, "book_tracker/authors.html#author-row", {"author": author})
    return render(request, "book_tracker/author_edit_row.html", {"author": author, "form": form})


# --- Book views ---


@require_GET
def book_list(request: HtmxHttpRequest) -> HttpResponse:
    books = Book.objects.prefetch_related("authors").order_by("title")
    form = BookForm()
    return render(request, "book_tracker/books.html", {"books": books, "form": form})


@require_POST
@require_htmx
def book_create(request: HtmxHttpRequest) -> HttpResponse:
    form = BookForm(request.POST)
    if form.is_valid():
        form.save()
        books = Book.objects.prefetch_related("authors").order_by("title")
        response = render(
            request,
            "book_tracker/books.html#book-list",
            {"books": books, "form": BookForm()},
        )
        response["HX-Retarget"] = "#book-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response
    return render(request, "book_tracker/books.html#book-form", {"form": form})


@require_GET
@require_htmx
def book_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book.objects.prefetch_related("authors"), pk=pk)
    return render(request, "book_tracker/books.html#book-row", {"book": book})


@require_GET
@require_htmx
def book_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(instance=book)
    return render(request, "book_tracker/book_edit_row.html", {"book": book, "form": form})


@require_POST
@require_htmx
def book_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST, instance=book)
    if form.is_valid():
        form.save()
        book = Book.objects.prefetch_related("authors").get(pk=pk)
        return render(request, "book_tracker/books.html#book-row", {"book": book})
    return render(request, "book_tracker/book_edit_row.html", {"book": book, "form": form})


# --- Section views ---


@require_GET
def section_list(request: HtmxHttpRequest) -> HttpResponse:
    sections = Section.objects.select_related("book").order_by("book__title", "order")
    form = SectionForm()
    return render(request, "book_tracker/sections.html", {"sections": sections, "form": form})


@require_POST
@require_htmx
def section_create(request: HtmxHttpRequest) -> HttpResponse:
    form = SectionForm(request.POST)
    if form.is_valid():
        form.save()
        sections = Section.objects.select_related("book").order_by("book__title", "order")
        response = render(
            request,
            "book_tracker/sections.html#section-list",
            {"sections": sections, "form": SectionForm()},
        )
        response["HX-Retarget"] = "#section-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response
    return render(request, "book_tracker/sections.html#section-form", {"form": form})


@require_GET
@require_htmx
def section_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section.objects.select_related("book"), pk=pk)
    return render(request, "book_tracker/sections.html#section-row", {"section": section})


@require_GET
@require_htmx
def section_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section, pk=pk)
    form = SectionForm(instance=section)
    return render(request, "book_tracker/section_edit_row.html", {"section": section, "form": form})


@require_POST
@require_htmx
def section_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    section = get_object_or_404(Section, pk=pk)
    form = SectionForm(request.POST, instance=section)
    if form.is_valid():
        form.save()
        section = Section.objects.select_related("book").get(pk=pk)
        return render(request, "book_tracker/sections.html#section-row", {"section": section})
    return render(request, "book_tracker/section_edit_row.html", {"section": section, "form": form})


# --- Exercise views ---


@require_GET
def exercise_list(request: HtmxHttpRequest) -> HttpResponse:
    exercises = (
        Exercise.objects.select_related("section__book")
        .prefetch_related("tags")
        .order_by(
            "section__book__title",
            "section__order",
            "identifier",
        )
    )
    form = ExerciseForm()
    return render(request, "book_tracker/exercises.html", {"exercises": exercises, "form": form})


@require_POST
@require_htmx
def exercise_create(request: HtmxHttpRequest) -> HttpResponse:
    form = ExerciseForm(request.POST)
    if form.is_valid():
        form.save()
        exercises = (
            Exercise.objects.select_related("section__book")
            .prefetch_related("tags")
            .order_by(
                "section__book__title",
                "section__order",
                "identifier",
            )
        )
        response = render(
            request,
            "book_tracker/exercises.html#exercise-list",
            {"exercises": exercises, "form": ExerciseForm()},
        )
        response["HX-Retarget"] = "#exercise-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response
    return render(request, "book_tracker/exercises.html#exercise-form", {"form": form})


@require_GET
@require_htmx
def exercise_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    return render(request, "book_tracker/exercises.html#exercise-row", {"exercise": exercise})


@require_GET
@require_htmx
def exercise_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise, pk=pk)
    form = ExerciseForm(instance=exercise)
    return render(request, "book_tracker/exercise_edit_row.html", {"exercise": exercise, "form": form})


@require_POST
@require_htmx
def exercise_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise, pk=pk)
    form = ExerciseForm(request.POST, instance=exercise)
    if form.is_valid():
        form.save()
        exercise = Exercise.objects.select_related("section__book").prefetch_related("tags").get(pk=pk)
        return render(request, "book_tracker/exercises.html#exercise-row", {"exercise": exercise})
    return render(request, "book_tracker/exercise_edit_row.html", {"exercise": exercise, "form": form})


@require_GET
def exercise_detail(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(
        Exercise.objects.select_related("section__book").prefetch_related("tags"),
        pk=pk,
    )
    stats = exercise.practice_logs.aggregate(
        practice_count=Count("id"),
        min_tempo=Min("tempo"),
        max_tempo=Max("tempo"),
        avg_tempo=Avg("tempo"),
        first_practiced=Min("practiced_on"),
        most_recent_practice=Max("practiced_on"),
        avg_difficulty=Avg("difficulty", filter=Q(difficulty__gt=0)),
        avg_relaxation=Avg("relaxation_level", filter=Q(relaxation_level__gt=0)),
    )
    last_log = exercise.practice_logs.order_by("-practiced_on", "-pk").first()
    recent_logs = exercise.practice_logs.order_by("-practiced_on", "-pk")[:10]
    return render(
        request,
        "book_tracker/exercise_detail.html",
        {"exercise": exercise, "stats": stats, "last_log": last_log, "recent_logs": recent_logs},
    )


@require_POST
def exercise_upload_notation(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise, pk=pk)
    form = NotationUploadForm(request.POST, request.FILES, instance=exercise)
    if form.is_valid():
        form.save()
    return redirect("exercise-detail", pk=pk)


def _parse_page_ranges(post_data: dict, start: int, end: int) -> dict[int, int] | list[str]:
    """Parse and validate page range rows from POST data.

    Returns a dict mapping exercise number → page number on success,
    or a list of error messages on failure.
    """
    range_starts = post_data.getlist("range_start")
    range_ends = post_data.getlist("range_end")
    range_pages = post_data.getlist("range_page")

    if not range_starts:
        return ["At least one page range is required."]

    errors: list[str] = []
    parsed: list[tuple[int, int, int]] = []

    for i, (rs, re_, rp) in enumerate(zip(range_starts, range_ends, range_pages, strict=False), 1):
        if not rs or not re_ or not rp:
            errors.append(f"Page range {i}: all fields are required.")
            continue
        try:
            rs_int, re_int, rp_int = int(rs), int(re_), int(rp)
        except ValueError:
            errors.append(f"Page range {i}: values must be integers.")
            continue
        if rs_int > re_int:
            errors.append(f"Page range {i}: 'from' ({rs_int}) must be ≤ 'to' ({re_int}).")
        elif rs_int < start or re_int > end:
            errors.append(f"Page range {i}: range {rs_int}-{re_int} is outside exercises {start}-{end}.")
        elif rp_int < 1:
            errors.append(f"Page range {i}: page number must be positive.")
        else:
            parsed.append((rs_int, re_int, rp_int))

    if errors:
        return errors

    # Check for overlaps
    parsed.sort()
    for i in range(len(parsed) - 1):
        if parsed[i][1] >= parsed[i + 1][0]:
            errors.append(
                f"Page ranges overlap: {parsed[i][0]}-{parsed[i][1]} and {parsed[i + 1][0]}-{parsed[i + 1][1]}.",
            )

    if errors:
        return errors

    # Check full coverage
    covered: set[int] = set()
    page_lookup: dict[int, int] = {}
    for rs_int, re_int, rp_int in parsed:
        for n in range(rs_int, re_int + 1):
            covered.add(n)
            page_lookup[n] = rp_int

    expected = set(range(start, end + 1))
    missing = expected - covered
    if missing:
        sorted_missing = sorted(missing)
        errors.append(f"Page ranges do not cover exercises: {', '.join(str(m) for m in sorted_missing)}.")
        return errors

    return page_lookup


def exercise_bulk_create(request: HtmxHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BulkExerciseCreateForm(request.POST)
        page_range_errors: list[str] = []

        if form.is_valid():
            section = form.cleaned_data["section"]
            start = form.cleaned_data["start"]
            end = form.cleaned_data["end"]
            tags = form.cleaned_data["tags"]

            result = _parse_page_ranges(request.POST, start, end)
            if isinstance(result, list):
                page_range_errors = result
            else:
                page_lookup = result

                for n in range(start, end + 1):
                    Exercise.objects.create(
                        section=section,
                        identifier=str(n),
                        page_number=page_lookup[n],
                    ).tags.set(tags)

                return redirect("exercise-list")

        # Re-render with errors - preserve page range rows from POST data
        range_starts = request.POST.getlist("range_start")
        range_ends = request.POST.getlist("range_end")
        range_pages = request.POST.getlist("range_page")
        page_ranges = list(zip(range_starts, range_ends, range_pages, strict=False))
        if not page_ranges:
            page_ranges = [("", "", "")]

        return render(
            request,
            "book_tracker/exercise_bulk_create.html",
            {"form": form, "page_ranges": page_ranges, "page_range_errors": page_range_errors},
        )

    form = BulkExerciseCreateForm()
    return render(
        request,
        "book_tracker/exercise_bulk_create.html",
        {"form": form, "page_ranges": [("", "", "")]},
    )


@require_GET
@require_htmx
def page_range_row(request: HtmxHttpRequest) -> HttpResponse:
    return render(request, "book_tracker/page_range_row.html")


# --- PracticeLog views ---


@require_GET
@require_htmx
def section_options(request: HtmxHttpRequest) -> HttpResponse:
    book_id = request.GET.get("book")
    exercise_target = request.GET.get("exercise_target", "id_exercise")
    if book_id:
        sections = Section.objects.filter(book_id=book_id).order_by("order")
        exercises = Exercise.objects.none()
    else:
        sections = Section.objects.none()
        exercises = Exercise.objects.none()
    return render(
        request,
        "book_tracker/section_options.html",
        {"sections": sections, "exercises": exercises, "exercise_target": exercise_target},
    )


@require_GET
@require_htmx
def exercise_options(request: HtmxHttpRequest) -> HttpResponse:
    book_id = request.GET.get("book")
    if book_id:
        exercises = (
            Exercise.objects.filter(
                section__book_id=book_id,
            )
            .select_related(
                "section",
                "section__book",
            )
            .order_by("section__order", "identifier")
        )
    else:
        exercises = Exercise.objects.none()
    return render(request, "book_tracker/exercise_options.html", {"exercises": exercises})


@require_GET
def practice_log_list(request: HtmxHttpRequest) -> HttpResponse:
    logs = PracticeLog.objects.select_related("exercise__section__book").order_by("-practiced_on", "-pk")
    form = PracticeLogForm()
    return render(request, "book_tracker/practice_logs.html", {"logs": logs, "form": form})


@require_POST
@require_htmx
def practice_log_create(request: HtmxHttpRequest) -> HttpResponse:
    form = PracticeLogForm(request.POST)
    if form.is_valid():
        log = form.save()
        logs = PracticeLog.objects.select_related("exercise__section__book").order_by("-practiced_on", "-pk")
        response = render(
            request,
            "book_tracker/practice_logs.html#log-list",
            {"logs": logs, "form": PracticeLogForm()},
        )
        response["HX-Retarget"] = "#log-list-container"
        response["HX-Reswap"] = "innerHTML"
        response["HX-Trigger"] = "logCreated"
        return response
    return render(request, "book_tracker/practice_logs.html#log-form", {"form": form})


@require_GET
@require_htmx
def practice_log_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog.objects.select_related("exercise__section__book"), pk=pk)
    return render(request, "book_tracker/practice_logs.html#log-row", {"log": log})


@require_GET
@require_htmx
def practice_log_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog, pk=pk)
    form = PracticeLogForm(instance=log)
    form.fields["exercise"].widget.attrs["id"] = f"edit-exercise-{log.id}"
    books = Book.objects.order_by("title")
    current_book_id = log.exercise.section.book_id
    current_section_id = log.exercise.section_id
    sections = Section.objects.filter(book_id=current_book_id).order_by("order")
    return render(
        request,
        "book_tracker/practice_log_edit_row.html",
        {
            "log": log,
            "form": form,
            "books": books,
            "sections": sections,
            "current_book_id": current_book_id,
            "current_section_id": current_section_id,
        },
    )


@require_POST
@require_htmx
def practice_log_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    log = get_object_or_404(PracticeLog, pk=pk)
    form = PracticeLogForm(request.POST, instance=log)
    if form.is_valid():
        log = form.save()
        log = PracticeLog.objects.select_related("exercise__section__book").get(pk=log.pk)
        return render(request, "book_tracker/practice_logs.html#log-row", {"log": log})
    books = Book.objects.order_by("title")
    book_id = request.POST.get("book") or log.exercise.section.book_id
    current_section_id = request.POST.get("section") or log.exercise.section_id
    sections = Section.objects.filter(book_id=book_id).order_by("order")
    form.fields["exercise"].widget.attrs["id"] = f"edit-exercise-{log.id}"
    return render(
        request,
        "book_tracker/practice_log_edit_row.html",
        {
            "log": log,
            "form": form,
            "books": books,
            "sections": sections,
            "current_book_id": book_id,
            "current_section_id": current_section_id,
        },
    )
