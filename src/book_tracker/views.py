from typing import TYPE_CHECKING, NamedTuple, TypedDict, TypeGuard

from django.db.models import Avg, Count, Max, Min, Q, QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from book_tracker.bulk_forms import build_form_rows
from book_tracker.forms import (
    AuthorForm,
    BulkExerciseCreateForm,
    NotationUploadForm,
    PracticeLogForm,
)
from book_tracker.models import Author, Exercise, Section
from core.htmx import require_htmx

if TYPE_CHECKING:
    from django.http import HttpResponse, QueryDict

    from core.htmx import HtmxHttpRequest

require_DELETE = require_http_methods(["DELETE"])  # noqa: N816


class PageRange(NamedTuple):
    start: int
    end: int
    page: int


class PageRangeFormRow(NamedTuple):
    range_start: str
    range_end: str
    range_page: str


class PageRangeRowParseResult(NamedTuple):
    page_range: PageRange | None
    error: str | None


class PageRangeParseSuccess(TypedDict):
    page_lookup: PageLookup


class PageLookup(TypedDict):
    exercise_to_page: dict[int, int]


class PageRangeParseFailure(TypedDict):
    errors: list[str]


PageRangeParseResultDict = PageRangeParseSuccess | PageRangeParseFailure


def _is_page_range_parse_failure(result: PageRangeParseResultDict) -> TypeGuard[PageRangeParseFailure]:
    return "errors" in result


def _is_page_range_parse_success(result: PageRangeParseResultDict) -> TypeGuard[PageRangeParseSuccess]:
    return "page_lookup" in result


# --- Author views ---


def get_authors() -> QuerySet[Author]:
    return Author.objects.order_by("last_name", "first_name")


@require_GET
def author_list(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/authors/list.html",
        {
            "authors": get_authors(),
            "form": AuthorForm(),
        },
    )


@require_GET
@require_htmx
def author_table_body(request: HtmxHttpRequest) -> HttpResponse:
    return render(
        request,
        "book_tracker/authors/_table_body.html",
        {"authors": get_authors()},
    )


@require_GET
@require_htmx
def author_row(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    return render(request, "book_tracker/authors/_row.html", {"author": author})


@require_POST
@require_htmx
def author_create(request: HtmxHttpRequest) -> HttpResponse:
    form = AuthorForm(request.POST)

    if form.is_valid():
        form.save()

        response = render(
            request,
            "book_tracker/authors/_list.html",
            {
                "authors": get_authors(),
                "form": AuthorForm(),
            },
        )
        response["HX-Retarget"] = "#author-list-container"
        response["HX-Reswap"] = "innerHTML"
        return response

    return render(
        request,
        "book_tracker/authors/_create_form.html",
        {"form": form},
        status=400,
    )


def author_edit(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(instance=author)

    return render(request, "book_tracker/authors/_row_form.html", {"author": author, "form": form})


@require_POST
@require_htmx
def author_update(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(request.POST, instance=author)

    if form.is_valid():
        form.save()
        return render(
            request,
            "book_tracker/authors/_table_body.html",
            {"authors": get_authors()},
        )

    return render(
        request,
        "book_tracker/authors/_row_form.html",
        {
            "author": author,
            "form": form,
        },
        status=400,
    )


@require_GET
@require_htmx
def author_confirm_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    return render(
        request,
        "book_tracker/authors/_row_confirm_delete.html",
        {"author": author},
    )


@require_DELETE
@require_htmx
def author_delete(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    author.delete()

    return render(
        request,
        "book_tracker/authors/_table_body.html",
        {"authors": get_authors()},
    )


# --- Exercise views ---


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
        "book_tracker/exercises/detail.html",
        {"exercise": exercise, "stats": stats, "last_log": last_log, "recent_logs": recent_logs},
    )


@require_POST
def exercise_upload_notation(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise, pk=pk)
    form = NotationUploadForm(request.POST, request.FILES, instance=exercise)
    if form.is_valid():
        form.save()
    return redirect("exercise-detail", pk=pk)


def _parse_page_range_row(  # noqa: PLR0913
    *,
    row_index: int,
    raw_start: str,
    raw_end: str,
    raw_page: str,
    exercise_start: int,
    exercise_end: int,
) -> PageRangeRowParseResult:
    if not raw_start or not raw_end or not raw_page:
        return PageRangeRowParseResult(page_range=None, error=f"Page range {row_index}: all fields are required.")

    try:
        start_int, end_int, page_int = int(raw_start), int(raw_end), int(raw_page)
    except ValueError:
        return PageRangeRowParseResult(page_range=None, error=f"Page range {row_index}: values must be integers.")

    if start_int > end_int:
        return PageRangeRowParseResult(
            page_range=None,
            error=f"Page range {row_index}: 'from' ({start_int}) must be ≤ 'to' ({end_int}).",
        )
    if start_int < exercise_start or end_int > exercise_end:
        return PageRangeRowParseResult(
            page_range=None,
            error=f"Page range {row_index}: range {start_int}-{end_int} is outside exercises {exercise_start}-{exercise_end}.",
        )
    if page_int < 1:
        return PageRangeRowParseResult(
            page_range=None,
            error=f"Page range {row_index}: page number must be positive.",
        )

    return PageRangeRowParseResult(page_range=PageRange(start=start_int, end=end_int, page=page_int), error=None)


def _find_page_range_overlaps(parsed_ranges: list[PageRange]) -> list[str]:
    if len(parsed_ranges) < 2:  # noqa: PLR2004
        return []

    overlaps: list[str] = []
    for i in range(len(parsed_ranges) - 1):
        current = parsed_ranges[i]
        nxt = parsed_ranges[i + 1]
        current_start, current_end = current.start, current.end
        next_start, next_end = nxt.start, nxt.end
        if current_end >= next_start:
            overlaps.append(f"Page ranges overlap: {current_start}-{current_end} and {next_start}-{next_end}.")
    return overlaps


def _build_page_lookup(parsed_ranges: list[PageRange]) -> tuple[set[int], dict[int, int]]:
    covered: set[int] = set()
    page_lookup: dict[int, int] = {}

    for page_range in parsed_ranges:
        for exercise_number in range(page_range.start, page_range.end + 1):
            covered.add(exercise_number)
            page_lookup[exercise_number] = page_range.page

    return covered, page_lookup


def _parse_page_ranges(post_data: QueryDict, start: int, end: int) -> PageRangeParseSuccess | PageRangeParseFailure:
    """
    Parse and validate page range rows from POST data.

    Returns a dict mapping exercise number → page number on success,
    or a list of error messages on failure.
    """
    range_start = post_data.getlist("range_start")
    range_end = post_data.getlist("range_end")
    range_page = post_data.getlist("range_page")

    if not range_start:
        return {"errors": ["At least one page range is required."]}

    errors: list[str] = []
    parsed_ranges: list[PageRange] = []

    for i, (rs, re_, rp) in enumerate(zip(range_start, range_end, range_page, strict=False), 1):
        parsed_row = _parse_page_range_row(
            row_index=i,
            raw_start=rs,
            raw_end=re_,
            raw_page=rp,
            exercise_start=start,
            exercise_end=end,
        )
        if parsed_row.error:
            errors.append(parsed_row.error)
            continue
        if parsed_row.page_range is not None:
            parsed_ranges.append(parsed_row.page_range)

    if errors:
        return {"errors": errors}

    parsed_ranges.sort()
    overlap_errors = _find_page_range_overlaps(parsed_ranges)
    if overlap_errors:
        return {"errors": overlap_errors}

    covered, page_lookup = _build_page_lookup(parsed_ranges)

    expected = set(range(start, end + 1))
    missing = expected - covered
    if missing:
        sorted_missing = sorted(missing)
        errors.append(f"Page ranges do not cover exercises: {', '.join(str(m) for m in sorted_missing)}.")
        return {"errors": errors}

    return {"page_lookup": {"exercise_to_page": page_lookup}}


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
            if _is_page_range_parse_failure(result):
                page_range_errors = result["errors"]
            elif _is_page_range_parse_success(result):
                page_lookup = result["page_lookup"]["exercise_to_page"]

                for n in range(start, end + 1):
                    Exercise.objects.create(
                        section=section,
                        identifier=str(n),
                        page_number=page_lookup[n],
                    ).tags.set(tags)

                return redirect("exercise-list")

        # Re-render with errors - preserve page range rows from POST data
        page_ranges = build_form_rows(
            request.POST,
            ("range_start", "range_end", "range_page"),
            PageRangeFormRow,
            PageRangeFormRow(range_start="", range_end="", range_page=""),
        )

        return render(
            request,
            "book_tracker/exercises/bulk_create.html",
            {"form": form, "page_ranges": page_ranges, "page_range_errors": page_range_errors},
        )

    form = BulkExerciseCreateForm()
    return render(
        request,
        "book_tracker/exercises/bulk_create.html",
        {"form": form, "page_ranges": [PageRangeFormRow(range_start="", range_end="", range_page="")]},
    )


@require_GET
@require_htmx
def page_range_row(request: HtmxHttpRequest) -> HttpResponse:
    return render(request, "book_tracker/exercises/_page_range_row.html")


# --- Practice log support views ---


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
        "book_tracker/logs/_section_options.html",
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
    return render(request, "book_tracker/logs/_exercise_options.html", {"exercises": exercises})


@require_POST
@require_htmx
def exercise_quick_log(request: HtmxHttpRequest, pk: str) -> HttpResponse:
    exercise = get_object_or_404(Exercise.objects.select_related("section__book"), pk=pk)
    # Prepopulate the form with the current exercise, section, and book
    data = request.POST.copy()
    data["exercise"] = str(exercise.pk)
    data["section"] = str(exercise.section.pk)
    data["book"] = str(exercise.section.book.pk)
    form = PracticeLogForm(data)
    if form.is_valid():
        form.save()
        form = PracticeLogForm()
    return render(request, "book_tracker/exercises/_quick_log_form.html", {"exercise": exercise, "form": form})
