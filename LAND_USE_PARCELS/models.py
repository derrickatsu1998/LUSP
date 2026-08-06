
# from datetime import timedelta
# import random
# import string

# from django.conf import settings
# from django.contrib.gis.db import models
# from django.contrib.gis.geos import Point
# from django.utils import timezone


# # ============================================================
# # PHOTO UPLOAD PATH
# # ============================================================

# def rename_photo(instance, filename):
#     """
#     Store parcel photos using the parcel ID and timestamp.

#     Example:
#         parcels/PARCEL001/20260803153045.jpg
#     """

#     extension = (
#         filename.rsplit(".", 1)[-1].lower()
#         if "." in filename
#         else "jpg"
#     )

#     return (
#         f"parcels/{instance.parcel_id}/"
#         f"{timezone.now():%Y%m%d%H%M%S}.{extension}"
#     )


# # ============================================================
# # PARCEL MODEL
# # ============================================================

# class Parcel(models.Model):

#     # --------------------------------------------------------
#     # LAND USE
#     # --------------------------------------------------------

#     LAND_USE_CHOICES = [
#         ("RES", "Residential"),
#         ("COM", "Commercial"),
#         ("MIX", "Mixed-Use"),
#         ("AGR", "Agriculture"),
#         ("VAC", "Vacant"),
#         ("WET", "Wetland"),
#     ]

#     # --------------------------------------------------------
#     # STRUCTURE STATUS
#     # --------------------------------------------------------

#     STATUS_CHOICES = [
#         ("COM", "Complete"),
#         ("UC", "Under Construction"),
#         ("UN", "Uncompleted/Roofed"),
#         ("COL", "Collapsed"),
#         ("NONE", "No Structure"),
#     ]

#     # --------------------------------------------------------
#     # IDENTIFICATION
#     # --------------------------------------------------------

#     parcel_id = models.CharField(
#         max_length=50,
#         primary_key=True,
#     )

#     parcel_name = models.CharField(
#         max_length=150,
#         blank=True,
#         default="",
#     )

#     section = models.CharField(
#         max_length=100,
#         blank=True,
#         default="",
#         help_text="Survey section or neighbourhood name.",
#     )

#     section_number = models.CharField(
#         max_length=50,
#         blank=True,
#         default="",
#         help_text="Survey section number.",
#     )

#     street = models.CharField(
#         max_length=150,
#         blank=True,
#         default="",
#     )

#     # --------------------------------------------------------
#     # WGS84 COORDINATES
#     #
#     # EPSG:4326
#     #
#     # longitude = X
#     # latitude  = Y
#     # --------------------------------------------------------

#     latitude = models.FloatField(
#         blank=True,
#         null=True,
#         help_text=(
#             "WGS84 latitude in decimal degrees "
#             "(EPSG:4326)"
#         ),
#     )

#     longitude = models.FloatField(
#         blank=True,
#         null=True,
#         help_text=(
#             "WGS84 longitude in decimal degrees "
#             "(EPSG:4326)"
#         ),
#     )

#     # --------------------------------------------------------
#     # GHANA WAR OFFICE / GHANA NATIONAL GRID
#     #
#     # EPSG:2136
#     #
#     # Values are stored in metres.
#     # --------------------------------------------------------

#     war_office_easting = models.FloatField(
#         blank=True,
#         null=True,
#         help_text=(
#             "Ghana War Office / Ghana National Grid "
#             "Easting in metres."
#         ),
#     )

#     war_office_northing = models.FloatField(
#         blank=True,
#         null=True,
#         help_text=(
#             "Ghana War Office / Ghana National Grid "
#             "Northing in metres."
#         ),
#     )

#     # --------------------------------------------------------
#     # POSTGIS GEOMETRY
#     #
#     # Authoritative spatial field.
#     #
#     # SRID 4326 = WGS84.
#     # --------------------------------------------------------

#     location = models.PointField(
#         geography=True,
#         srid=4326,
#         blank=True,
#         null=True,
#         help_text=(
#             "Parcel location in WGS84 "
#             "(EPSG:4326)."
#         ),
#     )

#     # --------------------------------------------------------
#     # LAND USE / PLANNING INFORMATION
#     # --------------------------------------------------------

#     master_plan_zone = models.CharField(
#         max_length=100,
#         blank=True,
#         default="",
#     )

#     field_land_use = models.CharField(
#         max_length=3,
#         choices=LAND_USE_CHOICES,
#         blank=True,
#         default="",
#     )

#     field_structure_status = models.CharField(
#         max_length=4,
#         choices=STATUS_CHOICES,
#         blank=True,
#         default="",
#     )

#     # --------------------------------------------------------
#     # FIELD SURVEY DATA
#     # --------------------------------------------------------

#     field_photo = models.ImageField(
#         upload_to=rename_photo,
#         blank=True,
#         null=True,
#     )

#     field_notes = models.TextField(
#         blank=True,
#         default="",
#     )

#     # --------------------------------------------------------
#     # VERIFICATION
#     # --------------------------------------------------------

#     is_verified = models.BooleanField(
#         default=False,
#     )

#     last_edited_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="edited_parcels",
#     )

#     date_visited = models.DateTimeField(
#         auto_now=True,
#     )

#     # --------------------------------------------------------
#     # SAVE
#     # --------------------------------------------------------

#     def save(self, *args, **kwargs):
#         """
#         Automatically create/update the PostGIS PointField
#         whenever latitude and longitude are available.

#         GeoJSON/PostGIS point order:
#             X = longitude
#             Y = latitude
#         """

#         if (
#             self.longitude is not None
#             and self.latitude is not None
#         ):
#             self.location = Point(
#                 float(self.longitude),
#                 float(self.latitude),
#                 srid=4326,
#             )

#         super().save(*args, **kwargs)

#     # --------------------------------------------------------
#     # DISPLAY
#     # --------------------------------------------------------

#     def __str__(self):
#         return f"Parcel {self.parcel_id}"


# # ============================================================
# # OTP MODEL
# # ============================================================

# class OTPCode(models.Model):

#     # --------------------------------------------------------
#     # USER
#     # --------------------------------------------------------

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="otp_codes",
#     )

#     # --------------------------------------------------------
#     # OTP CODE
#     # --------------------------------------------------------

#     code = models.CharField(
#         max_length=6,
#     )

#     # --------------------------------------------------------
#     # CREATION TIME
#     # --------------------------------------------------------

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     # --------------------------------------------------------
#     # USED STATUS
#     # --------------------------------------------------------

#     is_used = models.BooleanField(
#         default=False,
#     )

#     # --------------------------------------------------------
#     # OTP VALIDATION
#     # --------------------------------------------------------

#     def is_valid(self):
#         """
#         An OTP is valid when:

#         1. It has not already been used.
#         2. It is not older than 5 minutes.
#         """

#         if self.is_used:
#             return False

#         expiration_time = (
#             self.created_at
#             + timedelta(minutes=5)
#         )

#         return timezone.now() <= expiration_time

#     # --------------------------------------------------------
#     # OTP GENERATION
#     # --------------------------------------------------------

#     @staticmethod
#     def generate_otp():
#         """
#         Generate a random six-digit OTP.

#         Leading zeroes are allowed.
#         """

#         return "".join(
#             random.choices(
#                 string.digits,
#                 k=6,
#             )
#         )

#     # --------------------------------------------------------
#     # DISPLAY
#     # --------------------------------------------------------

#     def __str__(self):
#         return (
#             f"OTP for {self.user} "
#             f"({self.code})"
#         )

#     # --------------------------------------------------------
#     # MODEL OPTIONS
#     # --------------------------------------------------------

#     class Meta:
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(
#                 fields=["user", "is_used", "-created_at"]
#             ),
#         ]



from datetime import timedelta
import random
import string

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils import timezone


# ============================================================
# PHOTO UPLOAD PATH
# ============================================================

def rename_photo(instance, filename):
    """
    Store parcel photos using the parcel ID and timestamp.

    Example:
        parcels/PARCEL001/20260803153045.jpg
    """

    extension = (
        filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else "jpg"
    )

    return (
        f"parcels/{instance.parcel_id}/"
        f"{timezone.now():%Y%m%d%H%M%S}.{extension}"
    )


# ============================================================
# PARCEL MODEL
# ============================================================

class Parcel(models.Model):

    # --------------------------------------------------------
    # LAND USE
    # --------------------------------------------------------

    LAND_USE_CHOICES = [
        ("RES", "Residential"),
        ("COM", "Commercial"),
        ("MIX", "Mixed-Use"),
        ("AGR", "Agriculture"),
        ("VAC", "Vacant"),
        ("WET", "Wetland"),
    ]

    # --------------------------------------------------------
    # STRUCTURE STATUS
    # --------------------------------------------------------

    STATUS_CHOICES = [
        ("COM", "Complete"),
        ("UC", "Under Construction"),
        ("UN", "Uncompleted/Roofed"),
        ("COL", "Collapsed"),
        ("NONE", "No Structure"),
    ]

    # --------------------------------------------------------
    # IDENTIFICATION
    # --------------------------------------------------------

    parcel_id = models.CharField(
        max_length=50,
        primary_key=True,
    )

    parcel_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    section = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Survey section or neighbourhood name.",
    )

    section_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Survey section number.",
    )

    street = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    # --------------------------------------------------------
    # WGS84 COORDINATES
    #
    # EPSG:4326
    #
    # longitude = X
    # latitude  = Y
    # --------------------------------------------------------

    latitude = models.FloatField(
        blank=True,
        null=True,
        help_text=(
            "WGS84 latitude in decimal degrees "
            "(EPSG:4326)"
        ),
    )

    longitude = models.FloatField(
        blank=True,
        null=True,
        help_text=(
            "WGS84 longitude in decimal degrees "
            "(EPSG:4326)"
        ),
    )

    # --------------------------------------------------------
    # GHANA WAR OFFICE / GHANA NATIONAL GRID
    #
    # EPSG:2136
    #
    # Values are stored in metres.
    # --------------------------------------------------------

    war_office_easting = models.FloatField(
        blank=True,
        null=True,
        help_text=(
            "Ghana War Office / Ghana National Grid "
            "Easting in metres."
        ),
    )

    war_office_northing = models.FloatField(
        blank=True,
        null=True,
        help_text=(
            "Ghana War Office / Ghana National Grid "
            "Northing in metres."
        ),
    )

    # --------------------------------------------------------
    # POSTGIS GEOMETRY
    #
    # Authoritative spatial field.
    #
    # SRID 4326 = WGS84.
    # --------------------------------------------------------

    location = models.PointField(
        geography=True,
        srid=4326,
        blank=True,
        null=True,
        help_text=(
            "Parcel location in WGS84 "
            "(EPSG:4326)."
        ),
    )

    # --------------------------------------------------------
    # LAND USE / PLANNING INFORMATION
    # --------------------------------------------------------

    master_plan_zone = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    field_land_use = models.CharField(
        max_length=3,
        choices=LAND_USE_CHOICES,
        blank=True,
        default="",
    )

    field_structure_status = models.CharField(
        max_length=4,
        choices=STATUS_CHOICES,
        blank=True,
        default="",
    )

    # --------------------------------------------------------
    # FIELD SURVEY DATA
    # --------------------------------------------------------

    field_photo = models.ImageField(
        upload_to=rename_photo,
        blank=True,
        null=True,
    )

    field_notes = models.TextField(
        blank=True,
        default="",
    )

    # --------------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------------

    is_verified = models.BooleanField(
        default=False,
    )

    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_parcels",
    )

    date_visited = models.DateTimeField(
        auto_now=True,
    )


    section = models.CharField(max_length=100, blank=True, default='')
    section_number = models.CharField(max_length=50, blank='', default='')



    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, *args, **kwargs):
        """
        Automatically create/update the PostGIS PointField
        whenever latitude and longitude are available.

        GeoJSON/PostGIS point order:
            X = longitude
            Y = latitude
        """

        if (
            self.longitude is not None
            and self.latitude is not None
        ):
            self.location = Point(
                float(self.longitude),
                float(self.latitude),
                srid=4326,
            )

        super().save(*args, **kwargs)

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    def __str__(self):
        return f"Parcel {self.parcel_id}"


# ============================================================
# OTP MODEL
# ============================================================

class OTPCode(models.Model):

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_codes",
    )

    # --------------------------------------------------------
    # OTP CODE
    # --------------------------------------------------------

    code = models.CharField(
        max_length=6,
    )

    # --------------------------------------------------------
    # CREATION TIME
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # --------------------------------------------------------
    # USED STATUS
    # --------------------------------------------------------

    is_used = models.BooleanField(
        default=False,
    )

    # --------------------------------------------------------
    # OTP VALIDATION
    # --------------------------------------------------------

    def is_valid(self):
        """
        An OTP is valid when:

        1. It has not already been used.
        2. It is not older than 5 minutes.
        """

        if self.is_used:
            return False

        expiration_time = (
            self.created_at
            + timedelta(minutes=5)
        )

        return timezone.now() <= expiration_time

    # --------------------------------------------------------
    # OTP GENERATION
    # --------------------------------------------------------

    @staticmethod
    def generate_otp():
        """
        Generate a random six-digit OTP.

        Leading zeroes are allowed.
        """

        return "".join(
            random.choices(
                string.digits,
                k=6,
            )
        )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    def __str__(self):
        return (
            f"OTP for {self.user} "
            f"({self.code})"
        )

    # --------------------------------------------------------
    # MODEL OPTIONS
    # --------------------------------------------------------

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_used", "-created_at"]
            ),
        ]



def rename_structure_photo(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return (
        f"parcels/{instance.parcel.parcel_id}/structures/"
        f"structure_{instance.sequence:02d}_{timezone.now():%Y%m%d%H%M%S}.{extension}"
    )


class Structure(models.Model):
    TYPE_CHOICES = [
        ("SINGLE_ROOM", "Single room"),
        ("SELF_CONTAINED", "Self-contained"),
        ("SEMI_DETACHED", "Semi-detached"),
        ("DETACHED", "Detached"),
        ("COMPOUND", "Compound house"),
        ("APARTMENT", "Flat / apartment"),
        ("SHOP", "Shop / kiosk"),
        ("OTHER", "Other"),
    ]

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name="structures",
    )
    sequence = models.PositiveSmallIntegerField()
    structure_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    storeys = models.PositiveSmallIntegerField(blank=True, null=True)
    condition = models.CharField(
        max_length=4,
        choices=Parcel.STATUS_CHOICES,
        blank=True,
        default="",
    )
    notes = models.TextField(blank=True, default="")
    photo = models.ImageField(upload_to=rename_structure_photo, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["parcel", "sequence"],
                name="unique_structure_sequence_per_parcel",
            ),
        ]

    def __str__(self):
        return f"{self.parcel.parcel_id} – Structure {self.sequence}"



# LAND_USE_PARCELS/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ this is how you get the User model

class SavedParcelLayer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_layers'
    )
    name = models.CharField(max_length=200, default="My Parcels")
    geojson = models.JSONField()  # stores the full GeoJSON FeatureCollection
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"