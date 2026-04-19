FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput || true

# Start gunicorn with migrations at startup
# The migrations command runs first to handle database setup
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn placement_copilot.wsgi:application --bind 0.0.0.0:$PORT"]