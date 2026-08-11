FROM osgeo/gdal:3.9.0

# Add Python on top of the GDAL image
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-venv \
    libgeos-dev \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables for Django
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/libgeos_c.so

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]