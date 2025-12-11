#!/bin/bash
# Quick start script for the backend server

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting FastAPI server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

# Use app.main:app (not main:app) because the main.py is inside the app/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
