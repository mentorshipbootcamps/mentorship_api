from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserUpdate, UserResponse
from ..dependencies import get_current_admin, get_current_user, get_current_mentor, get_current_mentee, get_current_parent
from ..auth.utils import get_password_hash
import uuid

router = APIRouter(prefix="/users", tags=["users"])


# Admin endpoints
@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    return db.query(User).all()


@router.get("/mentees", response_model=List[UserResponse])
async def get_mentees(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all mentees (admin only)"""
    return db.query(User).filter(User.role == "mentee").all()


@router.get("/mentors", response_model=List[UserResponse])
async def get_mentors(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all mentors (admin only)"""
    return db.query(User).filter(User.role == "mentor").all()


@router.get("/parents", response_model=List[UserResponse])
async def get_parents(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all parents (admin only)"""
    return db.query(User).filter(User.role == "parent").all()


@router.post("/mentees", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_mentee(
    mentee_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new mentee (admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == mentee_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate mentee number if not provided
    if not mentee_data.mentee_number:
        mentees = db.query(User).filter(User.role == "mentee", User.mentee_number.isnot(None)).all()
        if mentees:
            numbers = [int(m.mentee_number.replace("MN", "")) for m in mentees if m.mentee_number and m.mentee_number.startswith("MN")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        mentee_number = f"MN{str(next_num).zfill(3)}"
    else:
        mentee_number = mentee_data.mentee_number
    
    new_mentee = User(
        id=str(uuid.uuid4()),
        name=mentee_data.name,
        email=mentee_data.email,
        password=get_password_hash(mentee_data.password),
        role="mentee",
        profile_picture=mentee_data.profile_picture,
        mentee_number=mentee_number,
        current_week=mentee_data.current_week or 1,
        completed_weeks=mentee_data.completed_weeks or [],
        mentor_id=mentee_data.mentor_id,
        parent_email=mentee_data.parent_email,
        parent_name=mentee_data.parent_name,
        parent_phone=mentee_data.parent_phone
    )
    
    db.add(new_mentee)
    db.commit()
    db.refresh(new_mentee)
    return UserResponse.from_orm(new_mentee)


@router.post("/mentors", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(
    mentor_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new mentor (admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == mentor_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate membership number if not provided
    if not mentor_data.membership_number:
        mentors = db.query(User).filter(User.role == "mentor", User.membership_number.isnot(None)).all()
        if mentors:
            numbers = [int(m.membership_number.replace("MEM", "")) for m in mentors if m.membership_number and m.membership_number.startswith("MEM")]
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        membership_number = f"MEM{str(next_num).zfill(3)}"
    else:
        membership_number = mentor_data.membership_number
    
    new_mentor = User(
        id=str(uuid.uuid4()),
        name=mentor_data.name,
        email=mentor_data.email,
        password=get_password_hash(mentor_data.password),
        role="mentor",
        profile_picture=mentor_data.profile_picture,
        membership_number=membership_number,
        specialization=mentor_data.specialization,
        bio=mentor_data.bio,
        assigned_mentees=mentor_data.assigned_mentees or []
    )
    
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    return UserResponse.from_orm(new_mentor)


@router.post("/parents", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent_data: UserCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new parent (admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == parent_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_parent = User(
        id=str(uuid.uuid4()),
        name=parent_data.name,
        email=parent_data.email,
        password=get_password_hash(parent_data.password),
        role="parent",
        profile_picture=parent_data.profile_picture,
        phone=parent_data.phone,
        children=parent_data.children or []
    )
    
    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)
    return UserResponse.from_orm(new_parent)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only view their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user (admin or self)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can only update their own profile unless they're admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return None


# Mentor endpoints
@router.get("/mentor/mentees", response_model=List[UserResponse])
async def get_assigned_mentees(
    current_user: User = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """Get mentees assigned to current mentor"""
    return db.query(User).filter(
        User.role == "mentee",
        User.mentor_id == current_user.id
    ).all()


# Parent endpoints
@router.get("/parent/children", response_model=List[UserResponse])
async def get_children(
    current_user: User = Depends(get_current_parent),
    db: Session = Depends(get_db)
):
    """Get children of current parent"""
    return db.query(User).filter(
        User.role == "mentee",
        User.parent_email == current_user.email
    ).all()


# Assignment endpoints
@router.post("/assign/{mentee_id}/{mentor_id}")
async def assign_mentee_to_mentor(
    mentee_id: str,
    mentor_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Assign mentee to mentor (admin only)"""
    mentee = db.query(User).filter(User.id == mentee_id, User.role == "mentee").first()
    mentor = db.query(User).filter(User.id == mentor_id, User.role == "mentor").first()
    
    if not mentee or not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentee or mentor not found"
        )
    
    # Remove from previous mentor if exists
    if mentee.mentor_id:
        prev_mentor = db.query(User).filter(User.id == mentee.mentor_id).first()
        if prev_mentor and prev_mentor.assigned_mentees:
            prev_mentor.assigned_mentees = [m for m in prev_mentor.assigned_mentees if m != mentee_id]
    
    # Assign to new mentor
    mentee.mentor_id = mentor_id
    if mentor.assigned_mentees is None:
        mentor.assigned_mentees = []
    if mentee_id not in mentor.assigned_mentees:
        mentor.assigned_mentees.append(mentee_id)
    
    db.commit()
    return {"message": "Mentee assigned successfully"}

