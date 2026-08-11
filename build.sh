#!/usr/bin/env bash
set -o errexit

# Install GDAL and GEOS (required for GeoDjango)
apt-get update && apt-get install -y gdal-bin libgdal-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate