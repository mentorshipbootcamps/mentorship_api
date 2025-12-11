#!/bin/bash
# Startup script for Render deployment
# Ensures server binds to 0.0.0.0 and uses PORT environment variable

PORT=${PORT:-10000}
uvicorn main:app --host 0.0.0.0 --port $PORT

