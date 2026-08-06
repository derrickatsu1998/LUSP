
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# ============================================================
# PROJECT URLS
# ============================================================

urlpatterns = [
    # Django administration
    path(
        "admin/",
        admin.site.urls,
    ),

    # Land Use Survey System application
    path(
        "",
        include("LAND_USE_PARCELS.urls"),
    ),
]


# ============================================================
# DEVELOPMENT MEDIA FILES
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

