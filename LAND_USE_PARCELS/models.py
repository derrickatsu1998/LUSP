import os
import json
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


# ============================================================
# HELPER FUNCTION FOR STRUCTURE PHOTO UPLOAD
# ============================================================

def rename_structure_photo(instance, filename):
    """Rename uploaded structure photos with a consistent pattern."""
    ext = filename.split('.')[-1]
    new_filename = f"structure_{instance.parcel.parcel_id}_{instance.sequence}.{ext}"
    return os.path.join("structure_photos/", new_filename)


# ============================================================
# OTP CODE
# ============================================================

class OTPCode(models.Model):
    """Six-digit one-time password for email authentication."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_codes",
    )

    code = models.CharField(
        max_length=6,
        help_text="Six-digit numeric code",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Whether this code has been used",
    )

    class Meta:
        verbose_name = "OTP Code"
        verbose_name_plural = "OTP Codes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"

    @classmethod
    def generate_otp(cls):
        """Generate a random 6-digit OTP."""
        import random
        return f"{random.randint(100000, 999999)}"

    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)."""
        if self.is_used:
            return False
        # Expires after 5 minutes
        expiry_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() <= expiry_time


# ============================================================
# PARCEL
# ============================================================

class Parcel(models.Model):
    """Land parcel with field survey data."""

    # Land use choices
    LAND_USE_CHOICES = [
        ("AGRICULTURE", "Agriculture"),
        ("COMMERCIAL", "Commercial"),
        ("INDUSTRIAL", "Industrial"),
        ("RESIDENTIAL", "Residential"),
        ("INSTITUTIONAL", "Institutional"),
        ("RECREATIONAL", "Recreational"),
        ("TRANSPORTATION", "Transportation"),
        ("UTILITY", "Utility"),
        ("VACANT", "Vacant"),
        ("OTHER", "Other"),
    ]

    # Structure status choices
    STATUS_CHOICES = [
        ("EXCELLENT", "Excellent"),
        ("GOOD", "Good"),
        ("FAIR", "Fair"),
        ("POOR", "Poor"),
        ("DILAPIDATED", "Dilapidated"),
        ("UNDER_CONSTRUCTION", "Under Construction"),
        ("VACANT", "Vacant"),
        ("DEMOLISHED", "Demolished"),
        ("NOT_APPLICABLE", "Not Applicable"),
    ]

    # Core fields
    parcel_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique parcel identifier",
    )

    parcel_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Parcel name or description",
    )

    # Location fields
    latitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Latitude in decimal degrees",
    )

    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Longitude in decimal degrees",
    )

    location = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text="PostGIS point geometry",
    )

    # Address fields
    section = models.CharField(
        max_length=100,
        blank=True,
        help_text="Section or neighborhood",
    )

    section_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Section number",
    )

    street = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address",
    )

    # Planning fields
    master_plan_zone = models.CharField(
        max_length=100,
        blank=True,
        help_text="Master plan zone designation",
    )

    # Field survey fields
    field_land_use = models.CharField(
        max_length=50,
        choices=LAND_USE_CHOICES,
        blank=True,
        help_text="Current land use observed in the field",
    )

    field_structure_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        blank=True,
        help_text="Current structure status observed in the field",
    )

    field_notes = models.TextField(
        blank=True,
        help_text="Additional field observation notes",
    )

    field_photo = models.ImageField(
        upload_to="parcel_photos/",
        null=True,
        blank=True,
        help_text="Field photo of the parcel",
    )

    # Verification fields
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this parcel has been field-verified",
    )

    date_visited = models.DateField(
        null=True,
        blank=True,
        help_text="Date of field visit",
    )

    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_parcels",
        help_text="User who last edited this parcel",
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this parcel record was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this parcel record was last updated",
    )

    class Meta:
        verbose_name = "Parcel"
        verbose_name_plural = "Parcels"
        ordering = ["parcel_id"]

    def __str__(self):
        return f"{self.parcel_id} - {self.parcel_name or 'Unnamed'}"

    def save(self, *args, **kwargs):
        """Save the parcel and update the PostGIS location field."""
        if self.latitude is not None and self.longitude is not None:
            self.location = Point(
                float(self.longitude),
                float(self.latitude),
                srid=4326,
            )
        else:
            self.location = None
        super().save(*args, **kwargs)

    @property
    def is_verified_display(self):
        """Return a human-readable verification status."""
        return "Verified" if self.is_verified else "Not Verified"


# ============================================================
# SAVED PARCEL LAYER
# ============================================================

class SavedParcelLayer(models.Model):
    """User-saved GeoJSON layers."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_layers",
    )

    name = models.CharField(
        max_length=255,
        help_text="Layer name",
    )

    geojson = models.JSONField(
        help_text="GeoJSON data for the layer",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Saved Layer"
        verbose_name_plural = "Saved Layers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.user.email}"


# ============================================================
# STRUCTURE
# ============================================================

class Structure(models.Model):
    """Building or structure on a parcel."""

    # Structure type choices
    TYPE_CHOICES = [
        ("RESIDENTIAL", "Residential Building"),
        ("COMMERCIAL", "Commercial Building"),
        ("INDUSTRIAL", "Industrial Building"),
        ("INSTITUTIONAL", "Institutional Building"),
        ("AGRICULTURAL", "Agricultural Structure"),
        ("STORAGE", "Storage Structure"),
        ("GARAGE", "Garage"),
        ("SHED", "Shed"),
        ("TEMPORARY", "Temporary Structure"),
        ("OTHER", "Other"),
    ]

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="structures",
    )

    sequence = models.PositiveIntegerField(
        help_text="Display order within the parcel",
    )

    structure_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text="Type of structure",
    )

    storeys = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Number of storeys",
    )

    condition = models.CharField(
        max_length=50,
        choices=Parcel.STATUS_CHOICES,
        blank=True,
        help_text="Condition of the structure",
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the structure",
    )

    photo = models.ImageField(
        upload_to=rename_structure_photo,  # ✅ Uses the helper function
        null=True,
        blank=True,
        help_text="Photo of the structure",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Structure"
        verbose_name_plural = "Structures"
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.get_structure_type_display()} - {self.parcel.parcel_id}"