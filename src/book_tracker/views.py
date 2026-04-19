from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from book_tracker.forms import AuthorForm, BookForm
from book_tracker.models import Author, Book
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
