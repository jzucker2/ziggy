FROM python:3.13.6-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Copy Gunicorn configuration
COPY gunicorn.conf.py .

# Make startup script executable
RUN chmod +x /app/start.sh

# Set default logging environment variables
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=default
ENV LOG_HANDLERS=console
ENV LOG_FILE=logs/app.log
ENV LOG_MAX_BYTES=10485760
ENV LOG_BACKUP_COUNT=5

# Expose the port the app runs on
EXPOSE 8000

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["/app/start.sh"]
