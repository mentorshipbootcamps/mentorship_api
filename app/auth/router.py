from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from ..database import get_supabase
from supabase import Client
from ..schemas import RegisterRequest, LoginRequest, LoginResponse, UserResponse, AdminCreateRequest
from ..dependencies import get_current_user
from .utils import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/create-admin", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def create_first_admin(admin_data: AdminCreateRequest, supabase: Client = Depends(get_supabase)):
    """Create the first admin user (only works if no admin exists)"""
    existing_admin_response = supabase.table("users").select("*").eq("role", "admin").execute()
    if existing_admin_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin user already exists. Use admin endpoints to create additional admins."
        )
    
    existing_user_response = supabase.table("users").select("*").eq("email", admin_data.email).execute()
    if existing_user_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    admin_data_dict = {
        "id": str(uuid.uuid4()),
        "name": admin_data.name,
        "email": admin_data.email,
        "password": get_password_hash(admin_data.password),
        "role": "admin"
    }
    
    response = supabase.table("users").insert(admin_data_dict).execute()
    admin = response.data[0]
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin["id"], "role": admin["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "user": UserResponse.model_validate(admin),
        "token": access_token
    }


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(register_data: RegisterRequest, supabase: Client = Depends(get_supabase)):
    """Register a new user"""
    if register_data.role not in ["mentee", "mentor", "parent"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'mentee', 'mentor', or 'parent'"
        )
    
    existing_user_response = supabase.table("users").select("*").eq("email", register_data.email).execute()
    if existing_user_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    mentee_number = None
    membership_number = None
    
    if register_data.role == "mentee":
        mentees_response = supabase.table("users").select("mentee_number").eq("role", "mentee").execute()
        if mentees_response.data:
            numbers = [int(m["mentee_number"].replace("MN", "")) for m in mentees_response.data if m.get("mentee_number") and m["mentee_number"] and m["mentee_number"].startswith("MN")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        mentee_number = f"MN{str(next_num).zfill(3)}"
    elif register_data.role == "mentor":
        mentors_response = supabase.table("users").select("membership_number").eq("role", "mentor").execute()
        if mentors_response.data:
            numbers = [int(m["membership_number"].replace("MEM", "")) for m in mentors_response.data if m.get("membership_number") and m["membership_number"] and m["membership_number"].startswith("MEM")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        membership_number = f"MEM{str(next_num).zfill(3)}"
    
    user_data = {
        "id": str(uuid.uuid4()),
        "name": register_data.name,
        "email": register_data.email,
        "password": get_password_hash(register_data.password),
        "role": register_data.role,
        "profile_picture": register_data.profile_picture,
        "mentee_number": mentee_number,
        "current_week": 1 if register_data.role == "mentee" else None,
        "completed_weeks": [] if register_data.role == "mentee" else None,
        "membership_number": membership_number,
        "specialization": register_data.specialization,
        "bio": register_data.bio,
        "phone": register_data.phone,
        "assigned_mentees": [] if register_data.role == "mentor" else None,
        "children": [] if register_data.role == "parent" else None
    }
    
    response = supabase.table("users").insert(user_data).execute()
    new_user = response.data[0]
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user["id"], "role": new_user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "user": UserResponse.model_validate(new_user),
        "token": access_token
    }


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, supabase: Client = Depends(get_supabase)):
    """Authenticate user and return JWT token"""
    response = supabase.table("users").select("*").eq("email", login_data.email).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = response.data[0]
    
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "user": UserResponse.model_validate(user),
        "token": access_token
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}

