from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from book_tracker.models import Author


class AuthorForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = Author
        fields = ("first_name", "last_name")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("first_name", "last_name")
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
