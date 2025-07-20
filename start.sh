#!/bin/bash

# Set default values
LOG_LEVEL=${LOG_LEVEL:-info}
ACCESS_LOG=${ACCESS_LOG:-true}

# Convert LOG_LEVEL to lowercase for Uvicorn
UVICORN_LOG_LEVEL=$(echo $LOG_LEVEL | tr '[:upper:]' '[:lower:]')

# Build Uvicorn command
UVICORN_CMD="uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level $UVICORN_LOG_LEVEL"

# Add access log configuration
if [ "$ACCESS_LOG" = "false" ]; then
    UVICORN_CMD="$UVICORN_CMD --no-access-log"
fi

echo "Starting Uvicorn with log level: $UVICORN_LOG_LEVEL"
echo "Command: $UVICORN_CMD"

exec $UVICORN_CMD
