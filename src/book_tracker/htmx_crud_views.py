from http import HTTPStatus
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from book_tracker.forms import BookForm, TagForm
from book_tracker.models import Book, Tag
from book_tracker.views import require_DELETE

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import QuerySet

    from core.htmx import HtmxHttpRequest


def require_htmx(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
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
