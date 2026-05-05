from django.urls import path

from book_tracker import views

app_name = "author"

urlpatterns = [
    path("", views.author_list, name="list"),
    path("create/", views.author_create, name="create"),
    path("<str:pk>/row/", views.author_row, name="row"),
    path("<str:pk>/edit/", views.author_edit, name="edit"),
    path("<str:pk>/update/", views.author_update, name="update"),
    path("<str:pk>/delete/", views.author_delete, name="delete"),
]
