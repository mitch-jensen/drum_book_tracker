from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from book_tracker.forms import AuthorForm, BookForm, ExerciseForm, PracticeLogForm, SectionForm
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
            "exercise_number",
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
                "exercise_number",
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


# --- PracticeLog views ---


@require_GET
@require_htmx
def section_options(request: HtmxHttpRequest) -> HttpResponse:
    book_id = request.GET.get("book")
    exercise_target = request.GET.get("exercise_target", "id_exercise")
    if book_id:
        sections = Section.objects.filter(book_id=book_id).order_by("order")
        exercises = Exercise.objects.filter(section__book_id=book_id).select_related("section").order_by("section__order", "exercise_number")
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
        exercises = Exercise.objects.filter(section__book_id=book_id).select_related("section").order_by("section__order", "exercise_number")
        section_id = request.GET.get("section")
        if section_id:
            exercises = exercises.filter(section_id=section_id)
        page_num = request.GET.get("page_number")
        if page_num:
            exercises = exercises.filter(page_number=page_num)
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
        form.save()
        logs = PracticeLog.objects.select_related("exercise__section__book").order_by("-practiced_on", "-pk")
        response = render(
            request,
            "book_tracker/practice_logs.html#log-list",
            {"logs": logs, "form": PracticeLogForm()},
        )
        response["HX-Retarget"] = "#log-list-container"
        response["HX-Reswap"] = "innerHTML"
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
        form.save()
        log = PracticeLog.objects.select_related("exercise__section__book").get(pk=pk)
        return render(request, "book_tracker/practice_logs.html#log-row", {"log": log})
    books = Book.objects.order_by("title")
    book_id = request.POST.get("book") or log.exercise.section.book_id
    current_section_id = request.POST.get("section") or log.exercise.section_id
    sections = Section.objects.filter(book_id=book_id).order_by("order")
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
