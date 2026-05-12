from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from django.http import QueryDict


def build_form_rows[T](
    post_data: QueryDict,
    field_names: Sequence[str],
    row_factory: Callable[..., T],
    empty_row: T,
) -> list[T]:
    values_by_field = (post_data.getlist(field_name) for field_name in field_names)
    rows = [row_factory(*values) for values in zip(*values_by_field, strict=False)]
    return rows or [empty_row]
