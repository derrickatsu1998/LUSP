

from pathlib import Path
import os
from decouple import Csv, config
import dj_database_url

# Force GDAL and GEOS paths for production
import os
# Force GDAL and GEOS library paths
if os.name != 'nt':
    GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so.30'
    GEOS_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/libgeos_c.so.1'

import sys

if os.name != 'nt':  # Linux environment
    try:
        import ctypes
        # Tell Django where to find GEOS
        from django.contrib.gis.geos import GEOSGeometry
        # Pre-load the library to ensure it's found
        geos_path = '/usr/lib/x86_64-linux-gnu/libgeos_c.so.1'
        ctypes.CDLL(geos_path)
        print(f"Successfully loaded GEOS from: {geos_path}")
    except Exception as e:
        print(f"Error loading GEOS: {e}")
        # Fallback to another possible location
        try:
            geos_path = '/usr/lib/libgeos_c.so.1'
            ctypes.CDLL(geos_path)
            print(f"Successfully loaded GEOS from: {geos_path}")
        except Exception as e2:
            print(f"Fallback also failed: {e2}")







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
# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-this-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())

# Add this - CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config(
    "DJANGO_CSRF_TRUSTED_ORIGINS", 
    default="https://lusp.onrender.com,https://*.onrender.com", 
    cast=Csv()
)

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
    "LAND_USE_PARCELS",  
    "session_security",          # Your app
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
    "session_security.middleware.SessionSecurityMiddleware", 
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
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "LAND_USE_PARCELS" / "TEMPLATES",  # Add this line
        ],
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

import os
import dj_database_url

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': os.environ.get('DB_NAME', 'landuse'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# # Or use DATABASE_URL (recommended)
# DATABASE_URL = os.environ.get('DATABASE_URL')
# if DATABASE_URL:
#     DATABASES['default'] = dj_database_url.config(
#         default=DATABASE_URL,
#         conn_max_age=600,
#         ssl_require=True
#     )



import sys

# ============================================================
# DATABASE – uses DATABASE_URL environment variable on Render
# ============================================================

import os
import dj_database_url

# Use DATABASE_URL for production (Render)
# If DATABASE_URL is set, use PostgreSQL
# Otherwise, fallback to SQLite for local development

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production on Render - use PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
    # Ensure PostGIS engine is used
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
else:
    # Local development - use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
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



# Session Security Settings
SESSION_SECURITY_WARN_AFTER = 840   # 14 minutes (warn user)
SESSION_SECURITY_EXPIRE_AFTER = 900  # 15 minutes (auto logout)
SESSION_SECURITY_PASSIVE_URLS = [
    r'^/admin/',
    r'^/static/',
    r'^/media/',
]