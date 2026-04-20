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
    path("sections/", views.section_list, name="section-list"),
    path("sections/create/", views.section_create, name="section-create"),
    path("sections/<str:pk>/", views.section_row, name="section-row"),
    path("sections/<str:pk>/edit/", views.section_edit, name="section-edit"),
    path("sections/<str:pk>/update/", views.section_update, name="section-update"),
    path("exercises/", views.exercise_list, name="exercise-list"),
    path("exercises/create/", views.exercise_create, name="exercise-create"),
    path("exercises/<str:pk>/", views.exercise_row, name="exercise-row"),
    path("exercises/<str:pk>/edit/", views.exercise_edit, name="exercise-edit"),
    path("exercises/<str:pk>/update/", views.exercise_update, name="exercise-update"),
    path("logs/", views.practice_log_list, name="log-list"),
    path("logs/create/", views.practice_log_create, name="log-create"),
    path("logs/section-options/", views.section_options, name="section-options"),
    path("logs/exercise-options/", views.exercise_options, name="exercise-options"),
    path("logs/<str:pk>/", views.practice_log_row, name="log-row"),
    path("logs/<str:pk>/edit/", views.practice_log_edit, name="log-edit"),
    path("logs/<str:pk>/update/", views.practice_log_update, name="log-update"),
]
