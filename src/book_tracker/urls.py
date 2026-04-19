from django.urls import path

from book_tracker import views

urlpatterns = [
    path("authors/", views.author_list, name="author-list"),
    path("authors/create/", views.author_create, name="author-create"),
    path("authors/<str:pk>/", views.author_row, name="author-row"),
    path("authors/<str:pk>/edit/", views.author_edit, name="author-edit"),
    path("authors/<str:pk>/update/", views.author_update, name="author-update"),
    path("books/", views.book_list, name="book-list"),
    path("books/create/", views.book_create, name="book-create"),
    path("books/<str:pk>/", views.book_row, name="book-row"),
    path("books/<str:pk>/edit/", views.book_edit, name="book-edit"),
    path("books/<str:pk>/update/", views.book_update, name="book-update"),
]
