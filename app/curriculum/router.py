from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import Dict, Any, List
from ..database import get_supabase
from ..schemas import WeekActivityCreate, WeekActivityResponse
from ..dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/weeks", response_model=List[WeekActivityResponse])
async def get_all_weeks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all week activities"""
    response = supabase.table("week_activities").select("*").order("week").execute()
    return [WeekActivityResponse.model_validate(week) for week in response.data]


@router.get("/weeks/{week_number}", response_model=WeekActivityResponse)
async def get_week_activity(
    week_number: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific week activity"""
    response = supabase.table("week_activities").select("*").eq("week", week_number).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    return WeekActivityResponse.model_validate(response.data[0])


@router.get("/bloc/{bloc_number}", response_model=List[WeekActivityResponse])
async def get_bloc_activities(
    bloc_number: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all activities for a specific bloc"""
    if bloc_number not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bloc number must be 1, 2, or 3"
        )
    response = supabase.table("week_activities").select("*").eq("bloc_number", bloc_number).order("week").execute()
    return [WeekActivityResponse.model_validate(week) for week in response.data]


@router.post("/weeks", response_model=WeekActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_week_activity(
    week_data: WeekActivityCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Create a new week activity (admin only)"""
    existing_response = supabase.table("week_activities").select("*").eq("week", week_data.week).execute()
    if existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Week {week_data.week} already exists"
        )
    
    week_dict = week_data.model_dump()
    response = supabase.table("week_activities").insert(week_dict).execute()
    return WeekActivityResponse.model_validate(response.data[0])


@router.put("/weeks/{week_number}", response_model=WeekActivityResponse)
async def update_week_activity(
    week_number: int,
    week_data: WeekActivityCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Update week activity (admin only)"""
    existing_response = supabase.table("week_activities").select("*").eq("week", week_number).execute()
    if not existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    
    update_data = week_data.model_dump()
    response = supabase.table("week_activities").update(update_data).eq("week", week_number).execute()
    return WeekActivityResponse.model_validate(response.data[0])


@router.delete("/weeks/{week_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_week_activity(
    week_number: int,
    current_user: Dict[str, Any] = Depends(get_current_admin),
    supabase: Client = Depends(get_supabase)
):
    """Delete week activity (admin only)"""
    existing_response = supabase.table("week_activities").select("*").eq("week", week_number).execute()
    if not existing_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Week {week_number} activity not found"
        )
    
    supabase.table("week_activities").delete().eq("week", week_number).execute()
    return None
