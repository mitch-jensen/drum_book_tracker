from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from health_check.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view()),
    path("", include("book_tracker.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
