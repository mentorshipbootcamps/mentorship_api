from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict, Any
from typing import List
from datetime import datetime
from ..database import get_supabase
from ..models import WeekApproval, User
from ..schemas import WeekApprovalCreate, WeekApprovalUpdate, WeekApprovalResponse
from ..dependencies import get_current_user, get_current_mentor, get_current_mentee
import uuid

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/", response_model=WeekApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_week_approval(
    approval_data: WeekApprovalCreate,
    current_user: Dict[str, Any] = Depends(get_current_mentee),
    supabase: Client = Depends(get_supabase)
):
    """Submit a week for approval (mentee only)"""
    # Verify mentee owns this approval
    if current_user.id != approval_data.mentee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit approvals for yourself"
        )
    
    # Check if mentee exists and has a mentor
    mentee = db.query(User).filter(User.id == approval_data.mentee_id).first()
    if not mentee or mentee.role != "mentee":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentee not found"
        )
    
    if not mentee.mentor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mentee has no assigned mentor"
        )
    
    # Check if approval already exists for this week
    existing = db.query(WeekApproval).filter(
        WeekApproval.mentee_id == approval_data.mentee_id,
        WeekApproval.week_number == approval_data.week_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval for week {approval_data.week_number} already exists"
        )
    
    new_approval = WeekApproval(
        id=str(uuid.uuid4()),
        mentee_id=approval_data.mentee_id,
        week_number=approval_data.week_number,
        mentor_id=mentee.mentor_id,
        status="pending",
        mentee_comment=approval_data.mentee_comment,
        mentee_comment_at=datetime.utcnow() if approval_data.mentee_comment else None
    )
    
    db.add(new_approval)
    db.commit()
    db.refresh(new_approval)
    return WeekApprovalResponse.from_orm(new_approval)


@router.get("/", response_model=List[WeekApprovalResponse])
async def get_week_approvals(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    status_filter: str = None
):
    """Get week approvals based on user role"""
    query = db.query(WeekApproval)
    
    if current_user.role == "mentee":
        query = query.filter(WeekApproval.mentee_id == current_user.id)
    elif current_user.role == "mentor":
        query = query.filter(WeekApproval.mentor_id == current_user.id)
    # Admin can see all
    
    if status_filter:
        query = query.filter(WeekApproval.status == status_filter)
    
    approvals = query.order_by(WeekApproval.submitted_at.desc()).all()
    return [WeekApprovalResponse.from_orm(a) for a in approvals]


@router.get("/pending", response_model=List[WeekApprovalResponse])
async def get_pending_approvals(
    current_user: Dict[str, Any] = Depends(get_current_mentor),
    supabase: Client = Depends(get_supabase)
):
    """Get pending approvals for current mentor"""
    approvals = db.query(WeekApproval).filter(
        WeekApproval.mentor_id == current_user.id,
        WeekApproval.status == "pending"
    ).order_by(WeekApproval.submitted_at.desc()).all()
    
    return [WeekApprovalResponse.from_orm(a) for a in approvals]


@router.get("/completed", response_model=List[WeekApprovalResponse])
async def get_completed_approvals(
    current_user: Dict[str, Any] = Depends(get_current_mentor),
    supabase: Client = Depends(get_supabase)
):
    """Get completed approvals for current mentor"""
    approvals = db.query(WeekApproval).filter(
        WeekApproval.mentor_id == current_user.id,
        WeekApproval.status == "approved"
    ).order_by(WeekApproval.approved_at.desc()).all()
    
    return [WeekApprovalResponse.from_orm(a) for a in approvals]


@router.get("/{approval_id}", response_model=WeekApprovalResponse)
async def get_approval(
    approval_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific approval"""
    approval = db.query(WeekApproval).filter(WeekApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin"]:
        if current_user.role == "mentee" and approval.mentee_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        if current_user.role == "mentor" and approval.mentor_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return WeekApprovalResponse.from_orm(approval)


@router.put("/{approval_id}/approve", response_model=WeekApprovalResponse)
async def approve_week(
    approval_id: str,
    approval_update: WeekApprovalUpdate,
    current_user: Dict[str, Any] = Depends(get_current_mentor),
    supabase: Client = Depends(get_supabase)
):
    """Approve a week (mentor only)"""
    approval = db.query(WeekApproval).filter(WeekApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    if approval.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only approve your own mentees' weeks"
        )
    
    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval is not pending"
        )
    
    approval.status = "approved"
    approval.mentor_feedback = approval_update.mentor_feedback
    approval.approved_at = datetime.utcnow()
    
    # Update mentee's completed weeks and current week
    mentee = db.query(User).filter(User.id == approval.mentee_id).first()
    if mentee:
        if mentee.completed_weeks is None:
            mentee.completed_weeks = []
        if approval.week_number not in mentee.completed_weeks:
            mentee.completed_weeks.append(approval.week_number)
        mentee.current_week = max(mentee.current_week or 1, approval.week_number + 1)
    
    db.commit()
    db.refresh(approval)
    return WeekApprovalResponse.from_orm(approval)


@router.put("/{approval_id}/reject", response_model=WeekApprovalResponse)
async def reject_week(
    approval_id: str,
    approval_update: WeekApprovalUpdate,
    current_user: Dict[str, Any] = Depends(get_current_mentor),
    supabase: Client = Depends(get_supabase)
):
    """Reject a week (mentor only)"""
    approval = db.query(WeekApproval).filter(WeekApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    if approval.mentor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only reject your own mentees' weeks"
        )
    
    approval.status = "rejected"
    approval.mentor_feedback = approval_update.mentor_feedback
    
    db.commit()
    db.refresh(approval)
    return WeekApprovalResponse.from_orm(approval)

