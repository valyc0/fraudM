FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/sql-rules && \
    chown -R 1000:1000 /app/logs /app/sql-rules

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Ensure app files have correct permissions
RUN chown -R 1000:1000 /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_DIR=/app

# Run the application
CMD ["python", "-u", "app/main.py"]