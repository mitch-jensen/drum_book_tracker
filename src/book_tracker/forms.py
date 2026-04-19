from django import forms

from book_tracker.models import Author


class AuthorForm(forms.ModelForm):
    class Meta:  # noqa: D106
        model = Author
        fields = ("first_name", "last_name")
