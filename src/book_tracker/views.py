from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from book_tracker.forms import AuthorForm
from book_tracker.models import Author
from core.htmx import require_htmx

if TYPE_CHECKING:
    from django.http import HttpResponse

    from core.htmx import HtmxHttpRequest


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
