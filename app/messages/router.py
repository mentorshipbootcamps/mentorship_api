from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict, Any
from typing import List
from datetime import datetime
from ..database import get_supabase
from ..schemas import MessageCreate, MessageResponse, MessageResponseRequest
from ..dependencies import get_current_user
import uuid

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Send a message"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.to_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found"
        )
    
    new_message = Message(
        id=str(uuid.uuid4()),
        from_id=current_user.id,
        to_id=message_data.to_id,
        subject=message_data.subject,
        content=message_data.content,
        type=message_data.type,
        week_number=message_data.week_number,
        status="awaiting_response"
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Get sender and recipient names for response
    response = MessageResponse(
        id=new_message.id,
        from_id=new_message.from_id,
        from_name=current_user.name,
        to_id=new_message.to_id,
        to_name=recipient.name,
        subject=new_message.subject,
        content=new_message.content,
        type=new_message.type,
        status=new_message.status,
        week_number=new_message.week_number,
        parent_message_id=new_message.parent_message_id,
        response=new_message.response,
        responded_at=new_message.responded_at,
        created_at=new_message.created_at
    )
    
    return response


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    status_filter: str = None
):
    """Get messages for current user"""
    query = db.query(Message).filter(
        (Message.from_id == current_user.id) | (Message.to_id == current_user.id)
    )
    
    if status_filter:
        query = query.filter(Message.status == status_filter)
    
    messages = query.order_by(Message.created_at.desc()).all()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.from_id).first()
        recipient = db.query(User).filter(User.id == msg.to_id).first()
        result.append(MessageResponse(
            id=msg.id,
            from_id=msg.from_id,
            from_name=sender.name if sender else "Unknown",
            to_id=msg.to_id,
            to_name=recipient.name if recipient else "Unknown",
            subject=msg.subject,
            content=msg.content,
            type=msg.type,
            status=msg.status,
            week_number=msg.week_number,
            parent_message_id=msg.parent_message_id,
            response=msg.response,
            responded_at=msg.responded_at,
            created_at=msg.created_at
        ))
    
    return result


@router.get("/sent", response_model=List[MessageResponse])
async def get_sent_messages(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get messages sent by current user"""
    messages = db.query(Message).filter(
        Message.from_id == current_user.id
    ).order_by(Message.created_at.desc()).all()
    
    result = []
    for msg in messages:
        recipient = db.query(User).filter(User.id == msg.to_id).first()
        result.append(MessageResponse(
            id=msg.id,
            from_id=msg.from_id,
            from_name=current_user.name,
            to_id=msg.to_id,
            to_name=recipient.name if recipient else "Unknown",
            subject=msg.subject,
            content=msg.content,
            type=msg.type,
            status=msg.status,
            week_number=msg.week_number,
            parent_message_id=msg.parent_message_id,
            response=msg.response,
            responded_at=msg.responded_at,
            created_at=msg.created_at
        ))
    
    return result


@router.get("/received", response_model=List[MessageResponse])
async def get_received_messages(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get messages received by current user"""
    messages = db.query(Message).filter(
        Message.to_id == current_user.id
    ).order_by(Message.created_at.desc()).all()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.from_id).first()
        result.append(MessageResponse(
            id=msg.id,
            from_id=msg.from_id,
            from_name=sender.name if sender else "Unknown",
            to_id=msg.to_id,
            to_name=current_user.name,
            subject=msg.subject,
            content=msg.content,
            type=msg.type,
            status=msg.status,
            week_number=msg.week_number,
            parent_message_id=msg.parent_message_id,
            response=msg.response,
            responded_at=msg.responded_at,
            created_at=msg.created_at
        ))
    
    return result


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check permissions
    if message.from_id != current_user.id and message.to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    sender = db.query(User).filter(User.id == message.from_id).first()
    recipient = db.query(User).filter(User.id == message.to_id).first()
    
    return MessageResponse(
        id=message.id,
        from_id=message.from_id,
        from_name=sender.name if sender else "Unknown",
        to_id=message.to_id,
        to_name=recipient.name if recipient else "Unknown",
        subject=message.subject,
        content=message.content,
        type=message.type,
        status=message.status,
        week_number=message.week_number,
        parent_message_id=message.parent_message_id,
        response=message.response,
        responded_at=message.responded_at,
        created_at=message.created_at
    )


@router.post("/{message_id}/respond", response_model=MessageResponse)
async def respond_to_message(
    message_id: str,
    response_data: MessageResponseRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Respond to a message"""
    original_message = db.query(Message).filter(Message.id == message_id).first()
    if not original_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if original_message.to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only respond to messages sent to you"
        )
    
    # Update original message
    original_message.status = "responded"
    original_message.response = response_data.response
    original_message.responded_at = datetime.utcnow()
    
    # Create reply message
    reply_type = original_message.type
    if "parent_to_mentor" in reply_type:
        reply_type = "mentor_to_parent"
    elif "mentor_to_parent" in reply_type:
        reply_type = "parent_to_mentor"
    
    reply_message = Message(
        id=str(uuid.uuid4()),
        from_id=current_user.id,
        to_id=original_message.from_id,
        subject=f"Re: {original_message.subject}",
        content=response_data.response,
        type=reply_type,
        week_number=original_message.week_number,
        parent_message_id=message_id,
        status="responded"
    )
    
    db.add(reply_message)
    db.commit()
    db.refresh(original_message)
    db.refresh(reply_message)
    
    recipient = db.query(User).filter(User.id == original_message.from_id).first()
    
    return MessageResponse(
        id=original_message.id,
        from_id=original_message.from_id,
        from_name=recipient.name if recipient else "Unknown",
        to_id=original_message.to_id,
        to_name=current_user.name,
        subject=original_message.subject,
        content=original_message.content,
        type=original_message.type,
        status=original_message.status,
        week_number=original_message.week_number,
        parent_message_id=original_message.parent_message_id,
        response=original_message.response,
        responded_at=original_message.responded_at,
        created_at=original_message.created_at
    )

