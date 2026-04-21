from django import template

register = template.Library()


@register.filter
def widget_sm(bound_field):
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
