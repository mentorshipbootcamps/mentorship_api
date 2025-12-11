from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str
    profile_picture: Optional[str] = None
    # Mentee fields
    mentee_number: Optional[str] = None
    current_week: Optional[int] = 1
    completed_weeks: Optional[List[int]] = []
    mentor_id: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    # Mentor fields
    membership_number: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None
    assigned_mentees: Optional[List[str]] = []
    # Parent fields
    phone: Optional[str] = None
    children: Optional[List[str]] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    current_week: Optional[int] = None
    completed_weeks: Optional[List[int]] = None
    mentor_id: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: str
    profile_picture: Optional[str]
    mentee_number: Optional[str]
    current_week: Optional[int]
    completed_weeks: Optional[List[int]]
    mentor_id: Optional[str]
    parent_email: Optional[str]
    parent_name: Optional[str]
    parent_phone: Optional[str]
    membership_number: Optional[str]
    specialization: Optional[str]
    bio: Optional[str]
    assigned_mentees: Optional[List[str]]
    phone: Optional[str]
    children: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    profile_picture: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    bio: Optional[str] = None


class AdminCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    token: str


class TokenData(BaseModel):
    user_id: str
    role: str


# Week Activity Schemas
class WeekActivityBase(BaseModel):
    week: int
    bloc_number: int
    sub_theme: str
    activity_name: str
    learning_outcome: str
    description: str
    digitization: str
    talent_indicators: List[str]


class WeekActivityCreate(WeekActivityBase):
    pass


class WeekActivityResponse(WeekActivityBase):
    class Config:
        from_attributes = True


# Week Approval Schemas
class WeekApprovalBase(BaseModel):
    mentee_id: str
    week_number: int
    mentee_comment: Optional[str] = None


class WeekApprovalCreate(WeekApprovalBase):
    pass


class WeekApprovalUpdate(BaseModel):
    status: Optional[str] = None
    mentor_feedback: Optional[str] = None


class WeekApprovalResponse(BaseModel):
    id: str
    mentee_id: str
    week_number: int
    status: str
    submitted_at: datetime
    mentor_id: str
    mentor_feedback: Optional[str]
    approved_at: Optional[datetime]
    mentee_comment: Optional[str]
    mentee_comment_at: Optional[datetime]

    class Config:
        from_attributes = True


# Message Schemas
class MessageBase(BaseModel):
    to_id: str
    subject: str
    content: str
    type: str
    week_number: Optional[int] = None


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    id: str
    from_id: str
    from_name: str
    to_id: str
    to_name: str
    subject: str
    content: str
    type: str
    status: str
    week_number: Optional[int]
    parent_message_id: Optional[str]
    response: Optional[str]
    responded_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponseRequest(BaseModel):
    message_id: str
    response: str


# Admin Review Schemas
class AdminReviewCreate(BaseModel):
    mentee_id: str
    week_number: int
    content: str


class AdminReviewResponse(BaseModel):
    id: str
    mentee_id: str
    mentee_name: str
    reviewer_id: str
    reviewer_name: str
    week_number: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# Mentor Feedback Schemas
class MentorFeedbackCreate(BaseModel):
    mentee_id: str
    week_number: int
    comment: str


class MentorFeedbackResponse(BaseModel):
    id: str
    mentee_id: str
    mentee_name: str
    mentor_id: str
    mentor_name: str
    week_number: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class DashboardStats(BaseModel):
    total_users: int
    mentees: int
    mentors: int
    parents: int
    completed_weeks: int
    bloc_completion: List[dict]
    weekly_progress: List[dict]
    mentor_mentee_ratio: float
    average_progress: int


# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    created_at: datetime
    read: bool

