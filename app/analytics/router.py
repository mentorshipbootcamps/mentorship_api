from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, WeekApproval
from ..schemas import DashboardStats
from ..dependencies import get_current_admin, get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (admin only)"""
    # Get user counts
    total_users = db.query(User).count()
    mentees = db.query(User).filter(User.role == "mentee").count()
    mentors = db.query(User).filter(User.role == "mentor").count()
    parents = db.query(User).filter(User.role == "parent").count()
    
    # Get all mentees with their completed weeks
    all_mentees = db.query(User).filter(User.role == "mentee").all()
    
    # Calculate total completed weeks
    total_completed_weeks = 0
    for mentee in all_mentees:
        if mentee.completed_weeks:
            total_completed_weeks += len(mentee.completed_weeks)
    
    # Calculate bloc completion
    bloc_completion = [
        {"bloc": 1, "name": "Artistic Inclination", "completed": 0, "total": 12},
        {"bloc": 2, "name": "Auditory Talents", "completed": 0, "total": 12},
        {"bloc": 3, "name": "Sensory Intelligence", "completed": 0, "total": 12}
    ]
    
    for mentee in all_mentees:
        if mentee.completed_weeks:
            for week in mentee.completed_weeks:
                if week <= 12:
                    bloc_completion[0]["completed"] += 1
                elif week <= 24:
                    bloc_completion[1]["completed"] += 1
                else:
                    bloc_completion[2]["completed"] += 1
    
    # Calculate weekly progress
    weekly_progress = []
    for week in range(1, 37):
        completions = sum(1 for mentee in all_mentees 
                         if mentee.completed_weeks and week in mentee.completed_weeks)
        weekly_progress.append({"week": week, "completions": completions})
    
    # Calculate ratios and averages
    mentor_mentee_ratio = mentees / mentors if mentors > 0 else 0
    average_progress = round((total_completed_weeks / (mentees * 36)) * 100) if mentees > 0 else 0
    
    return DashboardStats(
        total_users=total_users,
        mentees=mentees,
        mentors=mentors,
        parents=parents,
        completed_weeks=total_completed_weeks,
        bloc_completion=bloc_completion,
        weekly_progress=weekly_progress,
        mentor_mentee_ratio=round(mentor_mentee_ratio, 2),
        average_progress=average_progress
    )


@router.get("/mentor/stats")
async def get_mentor_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for current mentor"""
    if current_user.role != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access this endpoint"
        )
    
    assigned_mentees = db.query(User).filter(
        User.role == "mentee",
        User.mentor_id == current_user.id
    ).all()
    
    pending_approvals = db.query(WeekApproval).filter(
        WeekApproval.mentor_id == current_user.id,
        WeekApproval.status == "pending"
    ).count()
    
    completed_approvals = db.query(WeekApproval).filter(
        WeekApproval.mentor_id == current_user.id,
        WeekApproval.status == "approved"
    ).count()
    
    total_completed_weeks = sum(
        len(mentee.completed_weeks) if mentee.completed_weeks else 0 
        for mentee in assigned_mentees
    )
    
    return {
        "assigned_mentees": len(assigned_mentees),
        "pending_approvals": pending_approvals,
        "completed_approvals": completed_approvals,
        "total_completed_weeks": total_completed_weeks
    }

