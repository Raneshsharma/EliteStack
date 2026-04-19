FROM python:3.11-slim

WORKDIR /app

# Set placeholder SECRET_KEY for build-time (collectstatic needs it)
# Real SECRET_KEY is injected at runtime via env vars
ENV SECRET_KEY=placeholder-build-secret-not-for-production

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Start gunicorn with migrations at startup
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn placement_copilot.wsgi:application --bind 0.0.0.0:$PORT"]
