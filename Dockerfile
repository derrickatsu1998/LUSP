FROM python:3.11-slim-bullseye

# Install GDAL and GEOS
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Find and set the correct library paths
RUN echo "Finding GDAL..." && find /usr -name "libgdal.so*" 2>/dev/null
RUN echo "Finding GEOS..." && find /usr -name "libgeos_c.so*" 2>/dev/null

# Set environment variables with the actual paths
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]