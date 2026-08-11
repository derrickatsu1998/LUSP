FROM python:3.11-slim-bullseye

# Install GDAL and GEOS
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libgeos-c1v5 \
    && rm -rf /var/lib/apt/lists/*

# Find where GEOS is installed
RUN echo "=== Finding GEOS ===" && find /usr -name "libgeos*.so*" 2>/dev/null || echo "GEOS not found"

# Find where GDAL is installed
RUN echo "=== Finding GDAL ===" && find /usr -name "libgdal*.so*" 2>/dev/null || echo "GDAL not found"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]