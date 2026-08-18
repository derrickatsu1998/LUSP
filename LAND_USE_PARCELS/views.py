import json

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

from .models import OTPCode, Parcel, SavedParcelLayer, Structure

User = get_user_model()

# ============================================================
# GEOJSON HELPERS
# ============================================================

def parcel_feature(parcel):
    """Return a parcel as a WGS84 GeoJSON Feature."""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                float(parcel.longitude),
                float(parcel.latitude),
            ],
        }
        if (
            parcel.longitude is not None
            and parcel.latitude is not None
        )
        else None,
        "properties": {
            "parcel_id": parcel.parcel_id,
            "parcel_name": parcel.parcel_name,
            "section": parcel.section,
            "section_number": parcel.section_number,
            "street": parcel.street,
            "master_zone": parcel.master_plan_zone,
            "field_land_use": parcel.field_land_use,
            "field_land_use_display": (
                parcel.get_field_land_use_display()
                if parcel.field_land_use
                else "Not Verified"
            ),
            "field_structure_status": parcel.field_structure_status,
            "field_structure_status_display": (
                parcel.get_field_structure_status_display()
                if parcel.field_structure_status
                else "Not Recorded"
            ),
            "field_notes": parcel.field_notes,
            "photo_url": (
                parcel.field_photo.url
                if parcel.field_photo
                else None
            ),
            "verified": parcel.is_verified,
            "date_visited": (
                parcel.date_visited.isoformat()
                if parcel.date_visited
                else None
            ),
        },
    }

def structure_payload(structure):
    return {
        "id": structure.pk,
        "sequence": structure.sequence,
        "structure_type": structure.structure_type,
        "storeys": structure.storeys,
        "condition": structure.condition,
        "notes": structure.notes,
        "photo_url": structure.photo.url if structure.photo else None,
    }

# ============================================================
# AUTHENTICATION / REQUEST OTP
# ============================================================

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def request_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            import random
            otp = ''.join(random.choices('0123456789', k=6))
            request.session['otp'] = otp
            request.session['email'] = email
            # Send OTP (e.g., via Mailgun)...
            messages.success(request, "OTP sent to your email.")
            return redirect('verify_otp')
    return render(request, 'LAND_USE_PARCELS/request_otp.html')

# ============================================================
# VERIFY OTP
# ============================================================

# @ensure_csrf_cookie
# @require_http_methods(["GET", "POST"])
# def verify_otp_view(request):
#     email = request.session.get("otp_email")

#     if request.method == "GET":
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {"email": email})

#     if not email:
#         return redirect("request_otp")

#     code = request.POST.get("code", "").strip()
#     code = "".join(char for char in code if char.isdigit())

#     if len(code) != 6:
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {
#             "email": email,
#             "error": "Please enter the complete 6-digit verification code.",
#         })

#     user = User.objects.filter(email__iexact=email).first()
#     if user is None:
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {
#             "email": email,
#             "error": "User account could not be found. Please request a new verification code.",
#         })

#     otp = OTPCode.objects.filter(user=user, is_used=False).order_by("-created_at").first()
#     if otp is None:
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {
#             "email": email,
#             "error": "No active verification code was found. Please request a new code.",
#         })

#     if str(otp.code).strip() != code:
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {
#             "email": email,
#             "error": "Invalid verification code. Please enter the latest code sent to your email.",
#         })

#     if not otp.is_valid():
#         otp.is_used = True
#         otp.save(update_fields=["is_used"])
#         return render(request, "LAND_USE_PARCELS/verify_otp.html", {
#             "email": email,
#             "error": "This verification code has expired. Please request a new code.",
#         })

#     otp.is_used = True
#     otp.save(update_fields=["is_used"])

#     if hasattr(user, "is_active") and not user.is_active:
#         user.is_active = True
#         user.save(update_fields=["is_active"])

#     login(request, user)
#     request.session.pop("otp_email", None)
#     request.session.modified = True

#     return redirect("map_view")





from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

def verify_otp_view(request):
    if request.method == 'POST':
        # Combine the six OTP fields
        entered_otp = ''.join([request.POST.get(f'otp{i}', '') for i in range(1, 7)])
        stored_otp = request.session.get('otp')
        email = request.session.get('email')

        # Log everything for debugging
        logger.info(f"Entered: {entered_otp}, Stored: {stored_otp}, Email: {email}")

        # Validation: no OTP entered
        if not entered_otp:
            messages.error(request, "Please enter the 6-digit code.")
            return render(request, 'LAND_USE_PARCELS/verify_otp.html')

        # Validation: OTP expired
        if not stored_otp:
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect('request_otp')

        # OTP matches
        if entered_otp == stored_otp:
            try:
                user = User.objects.get(email=email)
                login(request, user)
                # Clear session
                request.session.pop('otp', None)
                request.session.pop('email', None)
                messages.success(request, "OTP verified successfully!")

                # Redirect to map (hardcoded path as fallback)
                return redirect('/map/')

            except User.DoesNotExist:
                messages.error(request, f"User with email '{email}' not found. Please request OTP again.")
                return render(request, 'LAND_USE_PARCELS/verify_otp.html')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'LAND_USE_PARCELS/verify_otp.html')

    return render(request, 'LAND_USE_PARCELS/verify_otp.html')

# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):
    logout(request)
    return redirect("request_otp")

# ============================================================
# MAP
# ============================================================

@login_required(login_url="request_otp")
def map_view(request):
    return render(request, "LAND_USE_PARCELS/map.html")

# ============================================================
# PARCEL GEOJSON API
# ============================================================

@login_required(login_url="request_otp")
@require_GET
def get_parcel_data(request):
    parcels = Parcel.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    features = [parcel_feature(parcel) for parcel in parcels]
    return JsonResponse({"type": "FeatureCollection", "features": features})

# ============================================================
# PARCEL SURVEY
# ============================================================

@login_required(login_url="request_otp")
@require_http_methods(["GET", "POST"])
def parcel_survey(request, parcel_id):
    if request.method == "GET":
        try:
            parcel = Parcel.objects.get(parcel_id=parcel_id)
        except Parcel.DoesNotExist:
            return JsonResponse({"parcel_id": parcel_id, "exists": False})

        return JsonResponse({
            "parcel_id": parcel.parcel_id,
            "exists": True,
            "parcel_name": parcel.parcel_name,
            "section": parcel.section,
            "section_number": parcel.section_number,
            "street": parcel.street,
            "master_plan_zone": parcel.master_plan_zone,
            "field_land_use": parcel.field_land_use,
            "field_land_use_display": (
                parcel.get_field_land_use_display() if parcel.field_land_use else "Not Verified"
            ),
            "field_structure_status": parcel.field_structure_status,
            "field_structure_status_display": (
                parcel.get_field_structure_status_display() if parcel.field_structure_status else "Not Recorded"
            ),
            "field_notes": parcel.field_notes,
            "field_photo_url": parcel.field_photo.url if parcel.field_photo else None,
            "is_verified": parcel.is_verified,
        })

    parcel, created = Parcel.objects.get_or_create(parcel_id=parcel_id)
    error = save_survey_fields(
        parcel=parcel,
        data=request.POST,
        files=request.FILES,
        user=request.user,
        photo_field="field_photo",
    )
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    return JsonResponse({
        "ok": True,
        "message": f"Parcel {parcel_id} saved successfully.",
        "created": created,
        "parcel": parcel_feature(parcel),
    })

# ============================================================
# SAVE SURVEY FIELDS
# ============================================================

def save_survey_fields(parcel, data, files, user, photo_field="field_photo"):
    allowed_land_uses = {value for value, _ in Parcel.LAND_USE_CHOICES}
    allowed_statuses = {value for value, _ in Parcel.STATUS_CHOICES}

    for field in ("parcel_name", "street", "section", "section_number", "field_notes"):
        if field in data:
            value = data.get(field, "").strip()
            setattr(parcel, field, value)

    for field in ("latitude", "longitude"):
        if field in data:
            value = data.get(field, "").strip()
            if not value:
                setattr(parcel, field, None)
                continue
            try:
                setattr(parcel, field, float(value))
            except (TypeError, ValueError):
                return f"Invalid {field} value."

    if "field_land_use" in data:
        value = data.get("field_land_use", "").strip()
        if value and value not in allowed_land_uses:
            return "Invalid land-use value."
        parcel.field_land_use = value

    if "field_structure_status" in data:
        value = data.get("field_structure_status", "").strip()
        if value and value not in allowed_statuses:
            return "Invalid structure-status value."
        parcel.field_structure_status = value

    if files.get(photo_field):
        parcel.field_photo = files[photo_field]

    parcel.is_verified = True
    parcel.last_edited_by = user
    parcel.save()
    return None

# ============================================================
# BACKWARDS-COMPATIBLE UPDATE API
# ============================================================

@login_required(login_url="request_otp")
@require_http_methods(["POST"])
def update_parcel(request):
    parcel_id = request.POST.get("parcel_id", "").strip()
    if not parcel_id:
        return JsonResponse({"success": False, "message": "parcel_id is required."}, status=400)

    parcel = get_object_or_404(Parcel, parcel_id=parcel_id)
    data = {
        "field_land_use": request.POST.get("land_use", ""),
        "field_structure_status": request.POST.get("status", ""),
        "field_notes": request.POST.get("notes", ""),
    }

    error = save_survey_fields(
        parcel=parcel,
        data=data,
        files=request.FILES,
        user=request.user,
        photo_field="photo",
    )
    if error:
        return JsonResponse({"success": False, "message": error}, status=400)

    return JsonResponse({
        "success": True,
        "message": f"Parcel {parcel_id} updated!",
        "parcel": parcel_feature(parcel),
    })

# ============================================================
# ZONES GEOJSON
# ============================================================

@login_required(login_url="request_otp")
@require_GET
def get_zones_geojson(request):
    parcels = Parcel.objects.exclude(master_plan_zone="").exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    features = []
    for parcel in parcels:
        feature = parcel_feature(parcel)
        feature["properties"] = {"zone": parcel.master_plan_zone, "parcel_id": parcel.parcel_id}
        features.append(feature)
    return JsonResponse({"type": "FeatureCollection", "features": features})

# ============================================================
# VERIFIED GEOJSON EXPORT
# ============================================================

@login_required(login_url="request_otp")
@require_GET
def export_verified_geojson(request):
    parcels = Parcel.objects.filter(is_verified=True).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    geojson = {"type": "FeatureCollection", "features": [parcel_feature(parcel) for parcel in parcels]}
    response = HttpResponse(
        json.dumps(geojson, indent=2, ensure_ascii=False),
        content_type="application/geo+json",
    )
    response["Content-Disposition"] = 'attachment; filename="verified_parcels.geojson"'
    return response

# ============================================================
# CONFORMANCE CHECK
# ============================================================

@login_required(login_url="request_otp")
@require_GET
def conformance_check(request, parcel_id):
    parcel = get_object_or_404(Parcel, parcel_id=parcel_id)
    return JsonResponse({
        "parcel_id": parcel.parcel_id,
        "master_plan_zone": parcel.master_plan_zone,
        "field_land_use": parcel.field_land_use,
        "field_land_use_display": (
            parcel.get_field_land_use_display() if parcel.field_land_use else None
        ),
        "field_structure_status": parcel.field_structure_status,
        "verified": parcel.is_verified,
        "conformance": "NOT_DETERMINED",
        "message": "A formal conformance result cannot be determined because the current database model does not contain planning-rule or permitted-use definitions.",
    })

# ============================================================
# SAVE STRUCTURES
# ============================================================

def save_structures(parcel, data, files):
    raw_value = data.get("structures_json", "[]")
    try:
        structures_data = json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        return "The structure list is invalid."

    if not isinstance(structures_data, list) or len(structures_data) > 50:
        return "Enter between 0 and 50 structures."

    allowed_types = {value for value, _ in Structure.TYPE_CHOICES}
    allowed_conditions = {value for value, _ in Parcel.STATUS_CHOICES}
    existing = {str(item.pk): item for item in parcel.structures.all()}
    submitted_ids = set()

    for item in structures_data:
        if not isinstance(item, dict) or item.get("structure_type") not in allowed_types:
            return "Choose a valid type for every structure."
        if item.get("condition") and item["condition"] not in allowed_conditions:
            return "Choose a valid condition for every structure."
        if item.get("storeys") not in (None, ""):
            try:
                if int(item["storeys"]) < 1:
                    return "Number of storeys must be at least 1."
            except (TypeError, ValueError):
                return "Number of storeys must be a whole number."

    for index, item in enumerate(structures_data):
        structure_id = str(item.get("id") or "")
        structure = existing.get(structure_id)
        if structure_id and structure is None:
            return "A submitted structure does not belong to this parcel."
        if structure is None:
            structure = Structure(parcel=parcel)

        structure.sequence = index + 1
        structure.structure_type = item["structure_type"]
        structure.storeys = int(item["storeys"]) if item.get("storeys") not in (None, "") else None
        structure.condition = item.get("condition", "")
        structure.notes = str(item.get("notes", "")).strip()
        photo = files.get(f"structure_photo_{index}")
        if photo:
            structure.photo = photo
        structure.save()
        submitted_ids.add(str(structure.pk))

    parcel.structures.exclude(pk__in=submitted_ids).delete()
    return None

# ============================================================
# SAVED LAYERS
# ============================================================

@login_required
@require_http_methods(["GET", "POST"])
def saved_layers(request):
    if request.method == "GET":
        layers = request.user.saved_layers.all().order_by('-created_at')
        data = [{
            "id": layer.id,
            "name": layer.name,
            "created_at": layer.created_at.isoformat(),
            "geojson": layer.geojson
        } for layer in layers]
        return JsonResponse({"layers": data})

    try:
        body = json.loads(request.body)
        name = body.get("name", "Untitled")
        geojson = body.get("geojson")
        if not geojson or not geojson.get("features"):
            return JsonResponse({"error": "Invalid GeoJSON"}, status=400)
        layer = SavedParcelLayer.objects.create(
            user=request.user,
            name=name,
            geojson=geojson
        )
        return JsonResponse({
            "id": layer.id,
            "name": layer.name,
            "created_at": layer.created_at.isoformat()
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_saved_layer(request, layer_id):
    try:
        layer = request.user.saved_layers.get(id=layer_id)
        layer.delete()
        return JsonResponse({"ok": True})
    except SavedParcelLayer.DoesNotExist:
        return JsonResponse({"error": "Layer not found"}, status=404)

# ============================================================
# ADMIN PARCEL VIEWER
# ============================================================

@staff_member_required
def admin_parcel_viewer(request):
    parcels = Parcel.objects.all().order_by('parcel_id')
    return render(request, 'admin/parcel_viewer.html', {'parcels': parcels})

# ============================================================
# PARCEL DETAIL VIEW (for GPS navigation)
# ============================================================

@login_required(login_url="request_otp")
def parcel_detail_view(request, parcel_id):
    parcel = get_object_or_404(Parcel, parcel_id=parcel_id)
    return render(request, 'LAND_USE_PARCELS/parcel_detail.html', {'parcel': parcel})


from django.contrib.auth import logout
from django.http import JsonResponse

@login_required
def check_session(request):
    """Check if session is still active."""
    return JsonResponse({'active': request.user.is_authenticated})

@login_required
def logout_inactive(request):
    """Logout due to inactivity."""
    logout(request)
    return JsonResponse({'logout': True})