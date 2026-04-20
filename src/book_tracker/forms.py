from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from book_tracker.models import Author, Book, Exercise, PracticeLog, Section


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


class BookForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = Book
        fields = ("title", "page_count", "authors")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("title", "page_count", "authors")
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class SectionForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = Section
        fields = ("book", "title", "order")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("book", "title", "order")
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class ExerciseForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = Exercise
        fields = ("section", "title", "exercise_number", "page_number", "tags")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("section", "title", "exercise_number", "page_number", "tags")
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class PracticeLogForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = PracticeLog
        fields = ("exercise", "practiced_on", "tempo", "difficulty", "relaxation_level", "notes")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("exercise", "practiced_on", "tempo", "difficulty", "relaxation_level", "notes")
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")
