import functools
from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

if TYPE_CHECKING:
    from collections.abc import Callable

    from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def require_htmx(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @functools.wraps(view_func)
    def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not getattr(request, "htmx", False):
            return HttpResponseBadRequest()
        return view_func(request, *args, **kwargs)

    return wrapped
