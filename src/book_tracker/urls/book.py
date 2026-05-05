from django.urls import path

from book_tracker import views

app_name = "book"

urlpatterns = [
    path("", views.book_list, name="list"),
    path("create/", views.book_create, name="create"),
    path("<str:pk>/", views.book_row, name="row"),
    path("<str:pk>/edit/", views.book_edit, name="edit"),
    path("<str:pk>/update/", views.book_update, name="update"),
]
