#!/usr/bin/env bash
set -o errexit

echo "=== Starting build.sh ==="

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input

echo "=== Running migrations ==="
python manage.py migrate

echo "=== build.sh finished ==="