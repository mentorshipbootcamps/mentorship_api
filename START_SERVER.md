# Starting the Backend Server

## Current Status

✅ Backend code is ready
✅ Dependencies installed
✅ .env file configured with your Supabase credentials
⚠️  Database connection may need verification

## To Start the Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The server will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## If You Get Database Connection Errors

1. **Get the exact connection string from Supabase:**
   - Go to: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/settings/database
   - Scroll to "Connection string" section
   - Copy the connection string from "URI" tab
   - Replace the DATABASE_URL in `.env` file

2. **Verify your project is active:**
   - Make sure your Supabase project is not paused
   - Check the project status in the dashboard

3. **Test the connection:**
   ```bash
   python test_connection.py
   ```

## Default Admin User

After the database is initialized, you can login with:
- Email: `admin@example.com`
- Password: `admin123`

**Important**: Change this password after first login!
