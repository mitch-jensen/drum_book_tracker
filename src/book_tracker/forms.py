from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.urls import reverse_lazy

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
    book = forms.ModelChoiceField(
        queryset=Book.objects.order_by("title"),
        required=False,
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("section-options"),
                "hx-target": "#id_section",
                "hx-include": "[name=book]",
                "hx-trigger": "change",
            },
        ),
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("exercise-options"),
                "hx-target": "#id_exercise",
                "hx-include": "[name=book],[name=section],[name=page_number]",
                "hx-trigger": "change",
            },
        ),
    )
    page_number = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "hx-get": reverse_lazy("exercise-options"),
                "hx-target": "#id_exercise",
                "hx-include": "[name=book],[name=section],[name=page_number]",
                "hx-trigger": "change",
            },
        ),
    )

    class Meta:  # noqa: D106
        model = PracticeLog
        fields = ("exercise", "practiced_on", "tempo", "difficulty", "relaxation_level", "notes")

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401, D107
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "book",
            "section",
            "page_number",
            "exercise",
            "practiced_on",
            "tempo",
            "difficulty",
            "relaxation_level",
            "notes",
        )

        book_id = None
        section_id = None

        if not self.instance._state.adding:  # noqa: SLF001
            book_id = self.instance.exercise.section.book_id
            section_id = self.instance.exercise.section_id
            self.fields["book"].initial = book_id
            self.fields["section"].initial = section_id
            if self.instance.exercise.page_number:
                self.fields["page_number"].initial = self.instance.exercise.page_number
        elif self.data:
            book_id = self.data.get("book") or None
            section_id = self.data.get("section") or None

        if book_id:
            self.fields["section"].queryset = Section.objects.filter(book_id=book_id).order_by("order")
            qs = (
                Exercise.objects.filter(
                    section__book_id=book_id,
                )
                .select_related("section")
                .order_by("section__order", "exercise_number")
            )
            if section_id:
                qs = qs.filter(section_id=section_id)
            page_num = self.data.get("page_number") if self.data else None
            if page_num:
                qs = qs.filter(page_number=page_num)
            self.fields["exercise"].queryset = qs
        else:
            self.fields["exercise"].queryset = Exercise.objects.none()

        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")

    def clean_page_number(self) -> int | None:
        """Validate page_number is within the selected book's page range."""
        page_num = self.cleaned_data.get("page_number")
        book = self.cleaned_data.get("book")
        if page_num and book and page_num > book.page_count:
            msg = f"Page number must be between 1 and {book.page_count}."
            raise forms.ValidationError(msg)
        return page_num
