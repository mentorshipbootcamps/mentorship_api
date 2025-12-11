# Get Your Supabase Connection String

## Quick Method (Recommended)

1. Go to: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/settings/database

2. Scroll down to "Connection string" section

3. Select "Connection pooling" tab (recommended)

4. Copy the connection string - it will look like:
   ```
   postgresql://postgres.xlkqhnssdyfxqjvtyxcp:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

5. Replace `[YOUR-PASSWORD]` with your database password (shown in the same page)

6. Paste it into the `.env` file as `DATABASE_URL=`

## Alternative: Use Direct Connection

If connection pooling doesn't work, use the "URI" tab instead:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xlkqhnssdyfxqjvtyxcp.supabase.co:5432/postgres
```

## After Setting DATABASE_URL

Run:
```bash
cd backend
source venv/bin/activate
python init_db.py  # Initialize database tables
uvicorn app.main:app --reload  # Start server
```
