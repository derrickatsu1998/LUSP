#!/usr/bin/env bash
set -o errexit

echo "=== Starting build.sh ==="

echo "=== Installing system GDAL ==="
apt-get update
apt-get install -y gdal-bin libgdal-dev
echo "=== GDAL installation complete ==="

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== Running migrations ==="
python manage.py migrate

echo "=== build.sh finished ==="