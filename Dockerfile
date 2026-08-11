FROM python:3.14-slim-bullseye

# Install GDAL system libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "LAND_USE_APP.wsgi:application"]