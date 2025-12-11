# Supabase Setup Guide

This guide will help you set up Supabase as your database for the Curriculum Development backend.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Your project name
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to your users
5. Click "Create new project"

## Step 2: Get Your Connection String

1. Once your project is created, go to **Settings** → **Database**
2. Scroll down to **Connection string**
3. Select **Connection pooling** (recommended for production)
4. Copy the connection string

The connection string will look like:
```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Or for direct connection:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## Step 3: Set Environment Variables

### Option 1: Using .env file (Recommended)

1. Create a `.env` file in the `backend` directory:
```bash
cd backend
touch .env
```

2. Add your connection string to the `.env` file:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres
SECRET_KEY=your-secret-key-change-in-production
```

**Important**: Replace `[YOUR-PASSWORD]` with your actual database password and `[PROJECT-REF]` with your project reference.

### Option 2: Using export (Linux/Mac)

```bash
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres"
export SECRET_KEY="your-secret-key-change-in-production"
```

### Option 3: Using set (Windows)

```cmd
set DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres
set SECRET_KEY=your-secret-key-change-in-production
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Initialize Database

```bash
python init_db.py
```

This will:
- Create all necessary database tables
- Create a default admin user (admin@example.com / admin123)

## Step 6: Start the Server

```bash
uvicorn app.main:app --reload
```

## Troubleshooting

### Connection Errors

**Error: "DATABASE_URL environment variable is required"**
- Make sure you've set the DATABASE_URL environment variable
- Check that your `.env` file is in the `backend` directory
- Restart your terminal/IDE after setting environment variables

**Error: "password authentication failed"**
- Verify your database password is correct
- If your password contains special characters, they should be URL-encoded
- Try using the connection string from Supabase dashboard directly

**Error: "could not connect to server"**
- Check that your Supabase project is active (not paused)
- Verify your network connection
- Make sure you're using the correct port (6543 for pooling, 5432 for direct)

### Password with Special Characters

If your password contains special characters like `@`, `#`, `$`, etc., they need to be URL-encoded:
- `@` becomes `%40`
- `#` becomes `%23`
- `$` becomes `%24`
- `&` becomes `%26`
- `+` becomes `%2B`
- `=` becomes `%3D`
- `?` becomes `%3F`

Or use the connection string directly from Supabase dashboard which handles this automatically.

### Using Connection Pooling vs Direct Connection

- **Connection Pooling (port 6543)**: Recommended for production, handles multiple connections efficiently
- **Direct Connection (port 5432)**: Simpler, but limited concurrent connections

## Security Notes

1. **Never commit your `.env` file** - It's already in `.gitignore`
2. **Change the default admin password** after first login
3. **Use strong passwords** for your Supabase database
4. **Rotate your SECRET_KEY** regularly in production
5. **Enable Row Level Security (RLS)** in Supabase for additional security

## Next Steps

- Set up database migrations with Alembic for production
- Configure Supabase Row Level Security policies
- Set up database backups
- Monitor your database usage in Supabase dashboard

