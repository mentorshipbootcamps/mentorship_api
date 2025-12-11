from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import WeekActivity
from ..schemas import WeekActivityCreate, WeekActivityResponse
from ..dependencies import get_current_user, get_current_admin
import uuid

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/weeks", response_model=List[WeekActivityResponse])
async def get_all_weeks(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all week activities"""
    return db.query(WeekActivity).order_by(WeekActivity.week).all()


@router.get("/weeks/{week_number}", response_model=WeekActivityResponse)
async def get_week_activity(
    week_number: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific week activity"""
    week_activity = db.query(WeekActivity).filter(WeekActivity.week == week_number).first()
    if not week_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    return WeekActivityResponse.from_orm(week_activity)


@router.get("/bloc/{bloc_number}", response_model=List[WeekActivityResponse])
async def get_bloc_activities(
    bloc_number: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all activities for a specific bloc"""
    if bloc_number not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bloc number must be 1, 2, or 3"
        )
    return db.query(WeekActivity).filter(
        WeekActivity.bloc_number == bloc_number
    ).order_by(WeekActivity.week).all()


@router.post("/weeks", response_model=WeekActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_week_activity(
    week_data: WeekActivityCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new week activity (admin only)"""
    # Check if week already exists
    existing = db.query(WeekActivity).filter(WeekActivity.week == week_data.week).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Week {week_data.week} already exists"
        )
    
    new_week = WeekActivity(**week_data.dict())
    db.add(new_week)
    db.commit()
    db.refresh(new_week)
    return WeekActivityResponse.from_orm(new_week)


@router.put("/weeks/{week_number}", response_model=WeekActivityResponse)
async def update_week_activity(
    week_number: int,
    week_data: WeekActivityCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update week activity (admin only)"""
    week_activity = db.query(WeekActivity).filter(WeekActivity.week == week_number).first()
    if not week_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    
    update_data = week_data.dict()
    for field, value in update_data.items():
        setattr(week_activity, field, value)
    
    db.commit()
    db.refresh(week_activity)
    return WeekActivityResponse.from_orm(week_activity)


@router.delete("/weeks/{week_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_week_activity(
    week_number: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete week activity (admin only)"""
    week_activity = db.query(WeekActivity).filter(WeekActivity.week == week_number).first()
    if not week_activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    
    db.delete(week_activity)
    db.commit()
    return None

