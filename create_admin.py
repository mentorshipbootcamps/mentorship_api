"""
Script to create an admin user using Supabase
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import supabase
from app.auth.utils import get_password_hash
import uuid

if not os.getenv("SUPABASE_ANON_KEY"):
    print("ERROR: SUPABASE_ANON_KEY environment variable is not set!")
    exit(1)

admin_email = "admin@gmail.com"
admin_password = "admin@gmail.com"

existing_admin_response = supabase.table("users").select("*").eq("email", admin_email).execute()

if existing_admin_response.data:
    existing_admin = existing_admin_response.data[0]
    print(f"User with email {admin_email} already exists")
    if existing_admin.get("role") != "admin":
        supabase.table("users").update({
            "role": "admin",
            "password": get_password_hash(admin_password)
        }).eq("id", existing_admin["id"]).execute()
        print(f"✓ Updated user to admin: {admin_email}")
    else:
        print("User is already an admin")
else:
    admin_data = {
        "id": str(uuid.uuid4()),
        "name": "Admin User",
        "email": admin_email,
        "password": get_password_hash(admin_password),
        "role": "admin"
    }
    response = supabase.table("users").insert(admin_data).execute()
    print(f"✓ Created admin user: {admin_email} / {admin_password}")

