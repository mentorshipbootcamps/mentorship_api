"""
Database initialization script
Run this to create the database and optionally seed with initial data

Make sure you have set the DATABASE_URL environment variable with your Supabase connection string.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import engine, Base, SessionLocal
from app.models import User, WeekActivity
from app.auth.utils import get_password_hash

# Check if DATABASE_URL is set
if not os.getenv("DATABASE_URL"):
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("\nPlease set your Supabase connection string:")
    print("export DATABASE_URL='postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres'")
    print("\nOr create a .env file with:")
    print("DATABASE_URL=postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:6543/postgres")
    exit(1)

try:
    print("Connecting to Supabase database...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

    db = SessionLocal()

    # Create default admin user if it doesn't exist
    admin = db.query(User).filter(User.email == "admin@gmail.com").first()
    if not admin:
        admin = User(
            id="admin1",
            name="Admin User",
            email="admin@gmail.com",
            password=get_password_hash("admin@gmail.com"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("✓ Created default admin user: admin@gmail.com / admin@gmail.com")
    else:
        print("✓ Admin user already exists")

    # Optionally seed curriculum data from the frontend
    # This would require reading the curriculum.ts file
    # For now, users can add curriculum data via the API

    db.close()
    print("\n✅ Database initialized successfully!")
    print("\nYou can now start the server with:")
    print("uvicorn app.main:app --reload")

except Exception as e:
    print(f"\n❌ Error initializing database: {e}")
    print("\nPlease check:")
    print("1. Your DATABASE_URL is correct")
    print("2. Your Supabase project is active")
    print("3. Your database password is correct")
    print("4. Your network connection is working")
    exit(1)

