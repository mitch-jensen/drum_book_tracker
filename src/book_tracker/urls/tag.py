from django.urls import path

from book_tracker import views

app_name = "tags"

urlpatterns = [
    path("", views.tag_list, name="list"),
    path("create/", views.tag_create, name="create"),
    path("<str:pk>/", views.tag_row, name="row"),
    path("<str:pk>/edit/", views.tag_edit, name="edit"),
    path("<str:pk>/update/", views.tag_update, name="update"),
]
