#!/usr/bin/env bash
set -o errexit

# Install GDAL system libraries
apt-get update
apt-get install -y gdal-bin libgdal-dev

# Set GDAL_CONFIG for pip to find GDAL
export GDAL_CONFIG=/usr/bin/gdal-config

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate