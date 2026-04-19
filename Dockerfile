FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations (conditionally — if no database, this will fail gracefully
# and the app will start anyway so we can set env vars later)
RUN bash -c "python manage.py migrate --noinput || true"
RUN bash -c "python manage.py collectstatic --noinput || true"

# Start gunicorn. Migrations run on startup in case DB was just attached.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn placement_copilot.wsgi:application --bind 0.0.0.0:$PORT"]
