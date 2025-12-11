#!/bin/bash
# Script to run the FastAPI backend server

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL environment variable is not set!"
    echo ""
    echo "Please set your Supabase connection string:"
    echo "  export DATABASE_URL='postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres'"
    echo ""
    echo "Or create a .env file in the backend directory with:"
    echo "  DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres"
    echo "  SECRET_KEY=your-secret-key-change-in-production"
    echo ""
    echo "See SUPABASE_SETUP.md for detailed instructions."
    exit 1
fi

# Check if SECRET_KEY is set
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  SECRET_KEY not set, using default (not recommended for production)"
    export SECRET_KEY="dev-secret-key-change-in-production"
fi

echo "🚀 Starting FastAPI server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
