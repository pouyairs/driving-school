"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import admin_reports


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),

    path("admin/reports/", admin_reports, name="admin_reports"),
    path("admin/", admin.site.urls),

    path("", include("core.urls")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("videos/", include("videos.urls")),
    path("quiz/", include("quiz.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "django_browser_reload" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]


handler404 = "core.views.custom_404"
