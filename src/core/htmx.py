import functools
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

if TYPE_CHECKING:
    from collections.abc import Callable

    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def require_htmx(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(view)
    def wrapper(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not hasattr(request, "htmx"):
            return HttpResponseBadRequest()
        return view(request, *args, **kwargs)

    return wrapper
