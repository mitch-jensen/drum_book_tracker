from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, render

from book_tracker.forms import AuthorForm
from book_tracker.models import Author

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def author_list(request: HttpRequest) -> HttpResponse:
    authors = Author.objects.order_by("last_name", "first_name")
    form = AuthorForm()
    return render(request, "book_tracker/authors.html", {"authors": authors, "form": form})


def author_create(request: HttpRequest) -> HttpResponse:
    form = AuthorForm(request.POST)
    if form.is_valid():
        form.save()
        authors = Author.objects.order_by("last_name", "first_name")
        return render(
            request,
            "book_tracker/authors.html#author-list",
            {"authors": authors, "form": AuthorForm()},
        )
    return render(request, "book_tracker/authors.html#author-form", {"form": form})


def author_row(request: HttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    return render(request, "book_tracker/authors.html#author-row", {"author": author})


def author_edit(request: HttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(instance=author)
    return render(request, "book_tracker/author_edit_row.html", {"author": author, "form": form})


def author_update(request: HttpRequest, pk: str) -> HttpResponse:
    author = get_object_or_404(Author, pk=pk)
    form = AuthorForm(request.POST, instance=author)
    if form.is_valid():
        form.save()
        return render(request, "book_tracker/authors.html#author-row", {"author": author})
    return render(request, "book_tracker/author_edit_row.html", {"author": author, "form": form})
