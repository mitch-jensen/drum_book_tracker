from django.contrib import admin

from book_tracker.models import Author, Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "page_count")
    search_fields = ("title",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")
