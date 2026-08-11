FROM python:3.11-slim-bullseye

# Install GDAL 3.2.2 system libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "LAND_USE_APP.wsgi:application"]