#!/usr/bin/env bash
set -o errexit

# Add GDAL repository for newer version
apt-get update
apt-get install -y software-properties-common
add-apt-repository ppa:ubuntugis/ubuntugis-unstable
apt-get update
apt-get install -y gdal-bin libgdal-dev

export GDAL_CONFIG=/usr/bin/gdal-config

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate