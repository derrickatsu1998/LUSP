from pathlib import Path
import os
from decouple import Csv, config
import dj_database_url



import os

# --- Force GDAL and GEOS paths for production ---
if os.name != 'nt':  # This means we are on a Linux system (like Render)
    # These paths were found by the 'find' command in your Docker build
    GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so.30'
    GEOS_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/libgeos_c.so.1'
# --- End of force paths ---







# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# QGIS / GDAL / GEOS CONFIGURATION (only needed for local Windows)
# ============================================================

import os

# GDAL/GEOS configuration
if os.name == 'nt':  # Windows (local)
    QGIS_BIN = r"C:\Program Files\QGIS 3.34.8\bin"
    if os.path.isdir(QGIS_BIN):
        try:
            os.add_dll_directory(QGIS_BIN)
        except (AttributeError, FileNotFoundError):
            pass
        os.environ["PATH"] = QGIS_BIN + os.pathsep + os.environ.get("PATH", "")
    GDAL_LIBRARY_PATH = os.path.join(QGIS_BIN, "gdal309.dll")
    GEOS_LIBRARY_PATH = os.path.join(QGIS_BIN, "geos_c.dll")
else:  # Linux (Render)
    GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH", "/usr/lib/libgdal.so")
    GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH", "/usr/lib/libgeos_c.so")

# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-this-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("DJANGO_CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",          # GeoDjango
    "anymail",                     # Email
    "LAND_USE_PARCELS",            # Your app
]

# ============================================================
# MIDDLEWARE (Whitenoise added for static files)
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # Must be high up
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "LAND_USE_APP.urls"
LOGIN_URL = "/request-otp/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/request-otp/"

# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "LAND_USE_APP.wsgi.application"

# ============================================================
# DATABASE – uses DATABASE_URL environment variable on Render
# ============================================================

# Default to local PostGIS settings if DATABASE_URL not set
default_db = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": "landuse",
    "USER": "postgres",
    "PASSWORD": config("DB_PASSWORD", default=""),
    "HOST": "localhost",
    "PORT": "5432",
}

DATABASES = {
    "default": dj_database_url.config(
        default=f"postgis://{default_db['USER']}:{default_db['PASSWORD']}@{default_db['HOST']}:{default_db['PORT']}/{default_db['NAME']}",
        conn_max_age=600,
        engine="django.contrib.gis.db.backends.postgis",
    )
}

# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Accra"
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC & MEDIA FILES
# ============================================================

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# EMAIL (Mailgun) – uses environment variables
# ============================================================

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": config("MAILGUN_API_KEY", default=""),
    "MAILGUN_SENDER_DOMAIN": config("MAILGUN_DOMAIN", default=""),
}
DEFAULT_FROM_EMAIL = f"postmaster@{config('MAILGUN_DOMAIN', default='example.com')}"