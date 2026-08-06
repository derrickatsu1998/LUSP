import os
import sys


# ============================================================
# QGIS / GDAL / GEOS DLL CONFIGURATION
# ============================================================

QGIS_BIN = r"C:\Program Files\QGIS 3.34.8\bin"

if os.path.isdir(QGIS_BIN):

    # Python 3.8+ DLL search path
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(QGIS_BIN)
        except (FileNotFoundError, OSError):
            pass

    # Put QGIS DLL directory first in PATH
    os.environ["PATH"] = (
        QGIS_BIN
        + os.pathsep
        + os.environ.get("PATH", "")
    )

    # Tell GeoDjango exactly which libraries to use
    os.environ["GDAL_LIBRARY_PATH"] = os.path.join(
        QGIS_BIN,
        "gdal309.dll"
    )

    os.environ["GEOS_LIBRARY_PATH"] = os.path.join(
        QGIS_BIN,
        "geos_c.dll"
    )


# ============================================================
# DJANGO SETTINGS
# ============================================================

def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "LAND_USE_APP.settings"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. "
            "Make sure Django is installed and your virtual "
            "environment is activated."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()