# Curriculum Development Backend API

FastAPI backend for the Curriculum Development Platform.

## Features

The backend is organized into feature-based modules:

- **Authentication** (`/auth`) - User login, logout, and token management
- **Users** (`/users`) - CRUD operations for mentees, mentors, parents, and admins
- **Curriculum** (`/curriculum`) - Week activities management
- **Approvals** (`/approvals`) - Week approval workflow
- **Messages** (`/messages`) - Messaging system between users
- **Notifications** (`/notifications`) - User notifications
- **Analytics** (`/analytics`) - Dashboard statistics and analytics

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Supabase:
   - Follow the detailed guide in [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
   - Or quickly: Create a project at [Supabase](https://supabase.com), get your connection string from Project Settings → Database
   - Use the "Connection pooling" option (port 6543) for better performance

3. Set environment variables:
   - Create a `.env` file in the `backend` directory (see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for details)
   - Or export them directly:
```bash
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres"
export SECRET_KEY="your-secret-key-change-in-production"
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

> **📖 Need help?** See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed Supabase setup instructions.

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Database

The application uses **Supabase** (PostgreSQL) as the database. 

### Getting Your Supabase Connection String

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **Database**
3. Under **Connection string**, select **Connection pooling** (recommended for production)
4. Copy the connection string and set it as the `DATABASE_URL` environment variable

**Connection String Formats:**
- **Direct connection**: `postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres`
- **Connection pooling** (recommended): `postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres`

**Note**: Replace `[PASSWORD]` with your database password and `[PROJECT-REF]` with your project reference ID.

### Database Tables

The application will automatically create all required tables on first run. Tables include:
- `users` - User accounts (mentees, mentors, parents, admins)
- `week_activities` - Curriculum week activities
- `week_approvals` - Week approval workflow
- `messages` - User messages
- `admin_reviews` - Admin reviews
- `mentor_feedbacks` - Mentor feedbacks

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints Overview

### Authentication
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout

### Users
- `GET /users` - Get all users (admin)
- `GET /users/mentees` - Get all mentees (admin)
- `GET /users/mentors` - Get all mentors (admin)
- `GET /users/parents` - Get all parents (admin)
- `POST /users/mentees` - Create mentee (admin)
- `POST /users/mentors` - Create mentor (admin)
- `POST /users/parents` - Create parent (admin)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user (admin)
- `GET /users/mentor/mentees` - Get assigned mentees (mentor)
- `GET /users/parent/children` - Get children (parent)
- `POST /users/assign/{mentee_id}/{mentor_id}` - Assign mentee to mentor (admin)

### Curriculum
- `GET /curriculum/weeks` - Get all week activities
- `GET /curriculum/weeks/{week_number}` - Get specific week
- `GET /curriculum/bloc/{bloc_number}` - Get bloc activities
- `POST /curriculum/weeks` - Create week activity (admin)
- `PUT /curriculum/weeks/{week_number}` - Update week (admin)
- `DELETE /curriculum/weeks/{week_number}` - Delete week (admin)

### Approvals
- `POST /approvals` - Submit week for approval (mentee)
- `GET /approvals` - Get approvals
- `GET /approvals/pending` - Get pending approvals (mentor)
- `GET /approvals/completed` - Get completed approvals (mentor)
- `GET /approvals/{approval_id}` - Get specific approval
- `PUT /approvals/{approval_id}/approve` - Approve week (mentor)
- `PUT /approvals/{approval_id}/reject` - Reject week (mentor)

### Messages
- `POST /messages` - Send message
- `GET /messages` - Get all messages
- `GET /messages/sent` - Get sent messages
- `GET /messages/received` - Get received messages
- `GET /messages/{message_id}` - Get specific message
- `POST /messages/{message_id}/respond` - Respond to message

### Notifications
- `GET /notifications` - Get notifications
- `GET /notifications/pending` - Get pending items

### Analytics
- `GET /analytics/dashboard` - Get dashboard stats (admin)
- `GET /analytics/mentor/stats` - Get mentor stats (mentor)

## Development

The database tables will be automatically created on first run when you execute `init_db.py` or start the application. 

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres
SECRET_KEY=your-secret-key-change-in-production
```

**Important**: Never commit your `.env` file to version control. The `.gitignore` file already excludes it.

### Database Migrations

For production, consider using Alembic for database migrations:
```bash
pip install alembic
alembic init alembic
```

### Troubleshooting

- **Connection errors**: Make sure your Supabase project is active and the connection string is correct
- **Password special characters**: If your password contains special characters, they may need to be URL-encoded
- **Connection pooling**: Use port 6543 for connection pooling (recommended) or port 5432 for direct connections

