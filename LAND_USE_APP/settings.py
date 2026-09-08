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
            # Your app
    # "session_security", 
               # Session security
    
    'rest_framework',
    'LAND_USE_PARCELS',

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
    # "session_security.middleware.SessionSecurityMiddleware",  # Session security
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

import os
import socket
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse the connection string manually
    parsed = urlparse(DATABASE_URL)
    db_name = parsed.path.lstrip('/')
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432

    # Resolve the hostname to an IPv4 address (ignores IPv6)
    ipv4 = None
    try:
        # Force IPv4 using AF_INET
        addrinfo = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if addrinfo:
            ipv4 = addrinfo[0][4][0]
            print(f"✅ Resolved {host} to IPv4: {ipv4}")
    except Exception as e:
        print(f"⚠️ Could not resolve IPv4: {e}")

    # Build the database config
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': db_name,
            'USER': user,
            'PASSWORD': password,
            'PORT': port,
            'CONN_MAX_AGE': 600,
        }
    }

    if ipv4:
        # Use IPv4 for the connection, but keep host for SSL certificate verification
        DATABASES['default']['HOST'] = ipv4
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
            'hostaddr': ipv4,           # force psycopg2 to use this IP
            'sslhost': host,            # verify SSL certificate against the domain
        }
    else:
        # Fallback to the hostname (may still use IPv6)
        DATABASES['default']['HOST'] = host
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }
else:
    # Local development – SQLite
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

# ============================================================
# ============================================================
# SESSION SECURITY
# ============================================================

# # Required for django-session-security
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_SECURITY_WARN_AFTER = 840   # 14 minutes (warn user)
# SESSION_SECURITY_EXPIRE_AFTER = 900  # 15 minutes (auto logout)

# # Fallback for session_security - required to prevent errors
# if not SESSION_EXPIRE_AT_BROWSER_CLOSE:
#     # This is only reached if SESSION_EXPIRE_AT_BROWSER_CLOSE is False
#     # but we set it to True above, so this is safe
#     pass

# # Optional: Disable session security warnings during build
# import sys
# if 'manage.py' in sys.argv[0] and 'collectstatic' in sys.argv:
#     # During collectstatic, we don't need session security
#     SESSION_SECURITY_INSECURE = True