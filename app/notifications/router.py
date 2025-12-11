from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict, Any
from typing import List
from ..database import get_supabase
from ..models import Message, WeekApproval, User
from ..schemas import NotificationResponse, WeekApprovalResponse, MessageResponse
from ..dependencies import get_current_user
import uuid

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get notifications for current user"""
    notifications = []
    
    if current_user.role == "mentor":
        # Get pending approvals
        pending_approvals = db.query(WeekApproval).filter(
            WeekApproval.mentor_id == current_user.id,
            WeekApproval.status == "pending"
        ).all()
        
        for approval in pending_approvals:
            mentee = db.query(User).filter(User.id == approval.mentee_id).first()
            notifications.append(NotificationResponse(
                id=approval.id,
                type="approval",
                title="Week approval pending",
                message=f"Week {approval.week_number} from {mentee.name if mentee else 'Unknown'} needs approval",
                created_at=approval.submitted_at,
                read=False
            ))
        
        # Get awaiting response messages
        awaiting_messages = db.query(Message).filter(
            Message.to_id == current_user.id,
            Message.status == "awaiting_response"
        ).all()
        
        for msg in awaiting_messages:
            sender = db.query(User).filter(User.id == msg.from_id).first()
            notifications.append(NotificationResponse(
                id=msg.id,
                type="message",
                title=f"New message from {sender.name if sender else 'Unknown'}",
                message=msg.subject,
                created_at=msg.created_at,
                read=False
            ))
    
    elif current_user.role == "parent":
        # Get awaiting response messages
        awaiting_messages = db.query(Message).filter(
            Message.to_id == current_user.id,
            Message.status == "awaiting_response"
        ).all()
        
        for msg in awaiting_messages:
            sender = db.query(User).filter(User.id == msg.from_id).first()
            notifications.append(NotificationResponse(
                id=msg.id,
                type="message",
                title=f"New message from {sender.name if sender else 'Unknown'}",
                message=msg.subject,
                created_at=msg.created_at,
                read=False
            ))
    
    elif current_user.role == "mentee":
        # Get approved weeks notifications
        approved_weeks = db.query(WeekApproval).filter(
            WeekApproval.mentee_id == current_user.id,
            WeekApproval.status == "approved"
        ).order_by(WeekApproval.approved_at.desc()).limit(5).all()
        
        for approval in approved_weeks:
            notifications.append(NotificationResponse(
                id=approval.id,
                type="approval",
                title="Week approved",
                message=f"Week {approval.week_number} has been approved",
                created_at=approval.approved_at or approval.submitted_at,
                read=False
            ))
    
    elif current_user.role == "admin":
        # Get all pending approvals
        pending_approvals = db.query(WeekApproval).filter(
            WeekApproval.status == "pending"
        ).all()
        
        for approval in pending_approvals:
            mentee = db.query(User).filter(User.id == approval.mentee_id).first()
            notifications.append(NotificationResponse(
                id=approval.id,
                type="approval",
                title="Week approval pending",
                message=f"Week {approval.week_number} from {mentee.name if mentee else 'Unknown'} needs approval",
                created_at=approval.submitted_at,
                read=False
            ))
        
        # Get awaiting response messages
        awaiting_messages = db.query(Message).filter(
            Message.status == "awaiting_response"
        ).all()
        
        for msg in awaiting_messages:
            sender = db.query(User).filter(User.id == msg.from_id).first()
            notifications.append(NotificationResponse(
                id=msg.id,
                type="message",
                title=f"New message from {sender.name if sender else 'Unknown'}",
                message=msg.subject,
                created_at=msg.created_at,
                read=False
            ))
    
    # Sort by created_at descending
    notifications.sort(key=lambda x: x.created_at, reverse=True)
    return notifications


@router.get("/pending", response_model=dict)
async def get_pending_items(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get pending items (approvals and messages)"""
    pending_approvals = []
    pending_messages = []
    
    if current_user.role == "mentor":
        approvals = db.query(WeekApproval).filter(
            WeekApproval.mentor_id == current_user.id,
            WeekApproval.status == "pending"
        ).all()
        pending_approvals = [WeekApprovalResponse.from_orm(a) for a in approvals]
        
        messages = db.query(Message).filter(
            Message.to_id == current_user.id,
            Message.status == "awaiting_response"
        ).all()
        pending_messages = [MessageResponse.from_orm(m) for m in messages]
    
    elif current_user.role == "admin":
        approvals = db.query(WeekApproval).filter(
            WeekApproval.status == "pending"
        ).all()
        pending_approvals = [WeekApprovalResponse.from_orm(a) for a in approvals]
        
        messages = db.query(Message).filter(
            Message.status == "awaiting_response"
        ).all()
        pending_messages = [MessageResponse.from_orm(m) for m in messages]
    
    return {
        "approvals": pending_approvals,
        "messages": pending_messages
    }

