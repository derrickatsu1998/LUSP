
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("LAND_USE_PARCELS.urls")),
    # Remove session_security for now to fix recursion
    # path("", include("session_security.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============================================================
# DEVELOPMENT MEDIA FILES
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

