
from django.urls import path

from . import views


urlpatterns = [
    # Main map
    path(
        "map/",
        views.map_view,
        name="map_view",
    ),

    # Authentication
    path(
        "request-otp/",
        views.request_otp_view,
        name="request_otp",
    ),

    path(
        "verify-otp/",
        views.verify_otp_view,
        name="verify_otp",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # Parcel API
    path(
        "api/parcels/",
        views.get_parcel_data,
        name="parcel_data",
    ),

    path(
        "api/parcels/<str:parcel_id>/survey/",
        views.parcel_survey,
        name="parcel_survey",
    ),

    path(
        "api/update/",
        views.update_parcel,
        name="update_parcel",
    ),

    # Zones
    path(
        "api/zones/",
        views.get_zones_geojson,
        name="zones",
    ),

    # GeoJSON export
    path(
        "export/geojson/",
        views.export_verified_geojson,
        name="export_geojson",
    ),

    # Conformance
    path(
        "api/conformance/<str:parcel_id>/",
        views.conformance_check,
        name="conformance",
    ),

    path(
    "",
    views.map_view,
    name="home",
    ),

    # urls.py
    path('api/saved-layers/', views.saved_layers, name='saved_layers'),
    path('api/saved-layers/<int:layer_id>/', views.delete_saved_layer, name='delete_saved_layer'),

    path('admin/parcel-viewer/', views.admin_parcel_viewer, name='admin_parcel_viewer'),

    path('parcel/<str:parcel_id>/', views.parcel_detail_view, name='parcel_detail'),
]


