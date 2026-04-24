from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.forms.boundfield import BoundField
    from django.utils.safestring import SafeText

register = template.Library()


@register.filter
def widget_sm(bound_field: BoundField) -> SafeText:
    """Render a form field widget with Bootstrap -sm classes and error styling."""
    attrs = bound_field.field.widget.attrs.copy()
    classes = attrs.get("class", "")
    if "form-select" in classes:
        classes += " form-select-sm"
    elif "form-control" in classes:
        classes += " form-control-sm"
    if bound_field.errors:
        classes += " is-invalid"
    attrs["class"] = classes.strip()
    return bound_field.as_widget(attrs=attrs)
