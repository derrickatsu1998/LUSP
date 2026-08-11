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

# Find and verify the GDAL library
RUN echo "=== Finding GDAL ===" && \
    find /usr -name "libgdal.so*" 2>/dev/null && \
    echo "=== Finding GEOS ===" && \
    find /usr -name "libgeos*.so*" 2>/dev/null

# Force the correct library path
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Debug: Check if GDAL exists before collectstatic
RUN ls -la /usr/lib/x86_64-linux-gnu/libgdal.so* || echo "GDAL not found in expected location"

RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]