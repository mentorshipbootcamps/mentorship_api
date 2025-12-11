# Supabase Setup Instructions

## Step 1: Create Database Tables

1. Go to your Supabase SQL Editor: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/sql/new

2. Copy the contents of `supabase_schema.sql` and paste it into the SQL editor

3. Click "Run" to create all the tables

## Step 2: Verify Environment Variables

Your `.env` file should have:
```env
SUPABASE_URL=https://xlkqhnssdyfxqjvtyxcp.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SECRET_KEY=dev-secret-key-change-in-production
```

## Step 3: Test Connection

```bash
python test_supabase.py
```

## Step 4: Create Admin User

```bash
python create_admin.py
```

This will create an admin user with:
- Email: `admin@gmail.com`
- Password: `admin@gmail.com`

## Step 5: Start the Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- **Create Admin**: `POST /auth/create-admin` (only works if no admin exists)
- **Register**: `POST /auth/register`
- **Login**: `POST /auth/login`
- **Get Current User**: `GET /auth/me`

## Notes

- The Supabase client uses the REST API, so no direct PostgreSQL connection is needed
- This avoids IPv6 connection issues
- All database operations go through Supabase's PostgREST API

