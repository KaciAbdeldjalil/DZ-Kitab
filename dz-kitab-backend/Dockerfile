FROM python:3.11-slim

# Install system dependencies for psycopg2 and other tools
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Permissions for start.sh
RUN chmod +x start.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Start script
CMD ["./start.sh"]
