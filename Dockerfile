FROM ubuntu:22.04

# Install Python, GDAL, and GEOS
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Set the correct library paths (found by the find command)
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so.30
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]