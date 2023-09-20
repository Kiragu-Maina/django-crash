# Use a base image with Python
FROM python:3.8

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the application code to the container
COPY . /app/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev 
    
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run database migrations and collect static files
RUN python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput

# Start the application using Daphne and Celery
CMD ["sh", "-c", "daphne -b 0.0.0.0 -p $PORT crashsite.asgi:application & python manage.py initadmin & python manage.py populate_users & celery -A crashsite beat & celery -A crashsite worker --loglevel=info"]
