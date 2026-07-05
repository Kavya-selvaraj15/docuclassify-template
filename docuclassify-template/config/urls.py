from django.urls import path, include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("apps.dashboard.urls")),
    path("documents/", include("apps.documents.urls")),
]

# Explicitly serve media files even with DEBUG=False.
# Django's built-in static() helper refuses to do this — this route
# bypasses that restriction directly. Fine for demo purposes; use
# cloud storage (S3 via django-storages) for real production use.
urlpatterns += [
    re_path("^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]