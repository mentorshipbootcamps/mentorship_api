from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from ..database import get_supabase
from supabase import Client
from ..schemas import UserCreate, UserUpdate, UserResponse
from ..dependencies import get_current_admin, get_current_user, get_current_mentor, get_current_mentee, get_current_parent
from ..auth.utils import get_password_hash
import uuid

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Get all users (admin only)"""
    response = supabase.table("users").select("*").execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.get("/mentees", response_model=List[UserResponse])
async def get_mentees(
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Get all mentees (admin only)"""
    response = supabase.table("users").select("*").eq("role", "mentee").execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.get("/mentors", response_model=List[UserResponse])
async def get_mentors(
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Get all mentors (admin only)"""
    response = supabase.table("users").select("*").eq("role", "mentor").execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.get("/parents", response_model=List[UserResponse])
async def get_parents(
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Get all parents (admin only)"""
    response = supabase.table("users").select("*").eq("role", "parent").execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.post("/mentees", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_mentee(
    mentee_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Create a new mentee (admin only)"""
    existing_response = supabase.table("users").select("*").eq("email", mentee_data.email).execute()
    if existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if not mentee_data.mentee_number:
        mentees_response = supabase.table("users").select("mentee_number").eq("role", "mentee").execute()
        if mentees_response.data:
            numbers = [int(m["mentee_number"].replace("MN", "")) for m in mentees_response.data if m.get("mentee_number") and m["mentee_number"] and m["mentee_number"].startswith("MN")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        mentee_number = f"MN{str(next_num).zfill(3)}"
    else:
        mentee_number = mentee_data.mentee_number
    
    user_data = {
        "id": str(uuid.uuid4()),
        "name": mentee_data.name,
        "email": mentee_data.email,
        "password": get_password_hash(mentee_data.password),
        "role": "mentee",
        "profile_picture": mentee_data.profile_picture,
        "mentee_number": mentee_number,
        "current_week": mentee_data.current_week or 1,
        "completed_weeks": mentee_data.completed_weeks or [],
        "mentor_id": mentee_data.mentor_id,
        "parent_email": mentee_data.parent_email,
        "parent_name": mentee_data.parent_name,
        "parent_phone": mentee_data.parent_phone
    }
    
    response = supabase.table("users").insert(user_data).execute()
    return UserResponse.model_validate(response.data[0])


@router.post("/mentors", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(
    mentor_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Create a new mentor (admin only)"""
    existing_response = supabase.table("users").select("*").eq("email", mentor_data.email).execute()
    if existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if not mentor_data.membership_number:
        mentors_response = supabase.table("users").select("membership_number").eq("role", "mentor").execute()
        if mentors_response.data:
            numbers = [int(m["membership_number"].replace("MEM", "")) for m in mentors_response.data if m.get("membership_number") and m["membership_number"] and m["membership_number"].startswith("MEM")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        membership_number = f"MEM{str(next_num).zfill(3)}"
    else:
        membership_number = mentor_data.membership_number
    
    user_data = {
        "id": str(uuid.uuid4()),
        "name": mentor_data.name,
        "email": mentor_data.email,
        "password": get_password_hash(mentor_data.password),
        "role": "mentor",
        "profile_picture": mentor_data.profile_picture,
        "membership_number": membership_number,
        "specialization": mentor_data.specialization,
        "bio": mentor_data.bio,
        "assigned_mentees": mentor_data.assigned_mentees or []
    }
    
    response = supabase.table("users").insert(user_data).execute()
    return UserResponse.model_validate(response.data[0])


@router.post("/parents", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Create a new parent (admin only)"""
    existing_response = supabase.table("users").select("*").eq("email", parent_data.email).execute()
    if existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_data = {
        "id": str(uuid.uuid4()),
        "name": parent_data.name,
        "email": parent_data.email,
        "password": get_password_hash(parent_data.password),
        "role": "parent",
        "profile_picture": parent_data.profile_picture,
        "phone": parent_data.phone,
        "children": parent_data.children or []
    }
    
    response = supabase.table("users").insert(user_data).execute()
    return UserResponse.model_validate(response.data[0])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user by ID"""
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = response.data[0]
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update user (admin or self)"""
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    response = supabase.table("users").update(update_data).eq("id", user_id).execute()
    return UserResponse.model_validate(response.data[0])


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Delete user (admin only)"""
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    supabase.table("users").delete().eq("id", user_id).execute()
    return None


@router.get("/mentor/mentees", response_model=List[UserResponse])
async def get_assigned_mentees(
    current_user: Dict[str, Any] = Depends(get_current_mentor),
    supabase: Client = Depends(get_supabase)
):
    """Get mentees assigned to current mentor"""
    response = supabase.table("users").select("*").eq("role", "mentee").eq("mentor_id", current_user.get("id")).execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.get("/parent/children", response_model=List[UserResponse])
async def get_children(
    current_user: Dict[str, Any] = Depends(get_current_parent),
    supabase: Client = Depends(get_supabase)
):
    """Get children of current parent"""
    response = supabase.table("users").select("*").eq("role", "mentee").eq("parent_email", current_user.get("email")).execute()
    return [UserResponse.model_validate(user) for user in response.data]


@router.post("/assign/{mentee_id}/{mentor_id}")
async def assign_mentee_to_mentor(
    mentee_id: str,
    mentor_id: str,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Assign mentee to mentor (admin only)"""
    mentee_response = supabase.table("users").select("*").eq("id", mentee_id).eq("role", "mentee").execute()
    mentor_response = supabase.table("users").select("*").eq("id", mentor_id).eq("role", "mentor").execute()
    
    if not mentee_response.data or not mentor_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentee or mentor not found"
        )
    
    mentee = mentee_response.data[0]
    mentor = mentor_response.data[0]
    
    if mentee.get("mentor_id"):
        prev_mentor_response = supabase.table("users").select("assigned_mentees").eq("id", mentee["mentor_id"]).execute()
        if prev_mentor_response.data:
            prev_mentor = prev_mentor_response.data[0]
            assigned_mentees = prev_mentor.get("assigned_mentees", []) or []
            assigned_mentees = [m for m in assigned_mentees if m != mentee_id]
            supabase.table("users").update({"assigned_mentees": assigned_mentees}).eq("id", mentee["mentor_id"]).execute()
    
    supabase.table("users").update({"mentor_id": mentor_id}).eq("id", mentee_id).execute()
    
    assigned_mentees = mentor.get("assigned_mentees", []) or []
    if mentee_id not in assigned_mentees:
        assigned_mentees.append(mentee_id)
    supabase.table("users").update({"assigned_mentees": assigned_mentees}).eq("id", mentor_id).execute()
    
    return {"message": "Mentee assigned successfully"}
