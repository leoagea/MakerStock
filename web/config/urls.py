from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("storage/", include("apps.storage.urls")),
    path("components/", include("apps.components.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("", include("apps.core.urls")),
]
