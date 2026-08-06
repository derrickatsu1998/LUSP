from django.contrib import admin
from django.http import HttpResponse
import json
import csv
from .models import OTPCode, Parcel, SavedParcelLayer, Structure

# ============================================================
# PARCEL ADMIN
# ============================================================

@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        'parcel_id', 'parcel_name', 'street', 'master_plan_zone',
        'field_land_use', 'field_structure_status', 'is_verified',
        'last_edited_by', 'date_visited'
    )
    search_fields = (
        'parcel_id', 'parcel_name', 'street', 'field_notes',
        'master_plan_zone', 'field_land_use'
    )
    list_filter = (
        'is_verified', 'field_land_use', 'field_structure_status',
        'master_plan_zone', 'date_visited'
    )
    # Only keep fields that actually exist on your model
    # Remove 'id' and 'location' if they cause errors
    readonly_fields = ('date_visited',)  # you can add back 'id' if it exists, but 'parcel_id' is the PK
    ordering = ('-date_visited',)

    # ---- Custom admin actions for export ----

    def export_geojson(self, request, queryset):
        features = []
        for parcel in queryset:
            if parcel.longitude is not None and parcel.latitude is not None:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(parcel.longitude), float(parcel.latitude)]
                    },
                    "properties": {
                        "parcel_id": parcel.parcel_id,
                        "parcel_name": parcel.parcel_name,
                        "street": parcel.street,
                        "master_plan_zone": parcel.master_plan_zone,
                        "field_land_use": parcel.field_land_use,
                        "field_structure_status": parcel.field_structure_status,
                        "field_notes": parcel.field_notes,
                        "is_verified": parcel.is_verified,
                        "date_visited": parcel.date_visited.isoformat() if parcel.date_visited else None,
                    }
                }
                features.append(feature)
        geojson = {"type": "FeatureCollection", "features": features}
        response = HttpResponse(json.dumps(geojson, indent=2), content_type='application/geo+json')
        response['Content-Disposition'] = 'attachment; filename="parcels.geojson"'
        return response
    export_geojson.short_description = "Export selected as GeoJSON"

    def export_csv(self, request, queryset):
        fields = [
            'parcel_id', 'parcel_name', 'street', 'master_plan_zone',
            'field_land_use', 'field_structure_status', 'field_notes',
            'is_verified', 'latitude', 'longitude', 'date_visited'
        ]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="parcels.csv"'
        writer = csv.writer(response)
        writer.writerow(fields)
        for obj in queryset:
            row = [getattr(obj, f, '') for f in fields]
            writer.writerow(row)
        return response
    export_csv.short_description = "Export selected as CSV"

    def export_wkt(self, request, queryset):
        wkt_lines = []
        for parcel in queryset:
            if parcel.longitude is not None and parcel.latitude is not None:
                # Manual WKT for a Point
                wkt = f"POINT({parcel.longitude} {parcel.latitude})"
                wkt_lines.append(f"{parcel.parcel_id}: {wkt}")
        content = "\n".join(wkt_lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="parcels.wkt"'
        return response
    export_wkt.short_description = "Export selected as WKT"

    def export_kml(self, request, queryset):
        kml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        kml += '<Document>\n'
        kml += '<name>Parcels</name>\n'
        for parcel in queryset:
            if parcel.longitude is not None and parcel.latitude is not None:
                kml += '<Placemark>\n'
                kml += f'<name>{parcel.parcel_id}</name>\n'
                kml += f'<description>{parcel.parcel_name}</description>\n'
                kml += f'<Point><coordinates>{parcel.longitude},{parcel.latitude}</coordinates></Point>\n'
                kml += '</Placemark>\n'
        kml += '</Document>\n'
        kml += '</kml>'
        response = HttpResponse(kml, content_type='application/vnd.google-earth.kml+xml')
        response['Content-Disposition'] = 'attachment; filename="parcels.kml"'
        return response
    export_kml.short_description = "Export selected as KML"

    def export_shapefile(self, request, queryset):
        self.message_user(
            request,
            "Shapefile export is not yet implemented. Please use GeoJSON export and convert using QGIS or ogr2ogr.",
            level='WARNING'
        )
        return self.export_geojson(request, queryset)
    export_shapefile.short_description = "Export selected as Shapefile (ZIP) – placeholder"

    actions = [export_geojson, export_csv, export_wkt, export_kml, export_shapefile]


# ============================================================
# STRUCTURE ADMIN
# ============================================================

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('parcel', 'sequence', 'structure_type', 'storeys', 'condition')
    list_filter = ('structure_type', 'condition')
    search_fields = ('parcel__parcel_id', 'parcel__parcel_name', 'notes')


# ============================================================
# OTP ADMIN
# ============================================================

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used', 'validity_status')
    search_fields = ('user__username', 'user__email', 'code')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def validity_status(self, obj):
        return "Valid" if obj.is_valid() else "Expired/Used"
    validity_status.short_description = "Status"


# ============================================================
# SAVED PARCEL LAYER ADMIN
# ============================================================

@admin.register(SavedParcelLayer)
class SavedParcelLayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__email')