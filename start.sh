#!/bin/bash

# Set default values for Gunicorn
LOG_LEVEL=${LOG_LEVEL:-info}
ACCESS_LOG=${ACCESS_LOG:-true}

# Convert LOG_LEVEL to lowercase for Gunicorn
GUNICORN_LOG_LEVEL=$(echo $LOG_LEVEL | tr '[:upper:]' '[:lower:]')

# Set Gunicorn environment variables
export GUNICORN_LOG_LEVEL=$GUNICORN_LOG_LEVEL

# Configure access log
if [ "$ACCESS_LOG" = "false" ]; then
    export GUNICORN_ACCESS_LOG=""
else
    export GUNICORN_ACCESS_LOG="-"
fi

# Build Gunicorn command
GUNICORN_CMD="gunicorn app.main:app --config gunicorn.conf.py"

echo "Starting Gunicorn with log level: $GUNICORN_LOG_LEVEL"
echo "Workers: ${GUNICORN_WORKERS:-$(nproc --all | awk '{print $1 * 2 + 1}')}"
echo "Command: $GUNICORN_CMD"

exec $GUNICORN_CMD
