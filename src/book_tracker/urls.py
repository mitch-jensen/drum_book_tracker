from django.urls import include, path

from book_tracker import views

app_name = "book_tracker"

urlpatterns = [
    path("authors/", include("book_tracker.urls.author")),
    path("tags/", include("book_tracker.urls.tag")),
    path("books/", include("book_tracker.urls.book")),
    path("sections/", views.section_list, name="section-list"),
    path("sections/create/", views.section_create, name="section-create"),
    path("sections/<str:pk>/", views.section_row, name="section-row"),
    path("sections/<str:pk>/edit/", views.section_edit, name="section-edit"),
    path("sections/<str:pk>/update/", views.section_update, name="section-update"),
    path("exercises/", views.exercise_list, name="exercise-list"),
    path("exercises/create/", views.exercise_create, name="exercise-create"),
    path("exercises/bulk-create/", views.exercise_bulk_create, name="exercise-bulk-create"),
    path("exercises/page-range-row/", views.page_range_row, name="page-range-row"),
    path("exercises/<str:pk>/", views.exercise_row, name="exercise-row"),
    path("exercises/<str:pk>/detail/", views.exercise_detail, name="exercise-detail"),
    path("exercises/<str:pk>/detail/quick-log/", views.exercise_quick_log, name="exercise-quick-log"),
    path("exercises/<str:pk>/upload-notation/", views.exercise_upload_notation, name="exercise-upload-notation"),
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
