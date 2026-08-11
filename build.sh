#!/usr/bin/env bash
set -o errexit

# Install GDAL and GEOS (required for GeoDjango)
apt-get update && apt-get install -y gdal-bin libgdal-dev

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate