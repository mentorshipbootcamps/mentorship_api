from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Should be hashed
    role = Column(String, nullable=False)  # mentee, mentor, parent, admin
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Mentee specific fields
    mentee_number = Column(String, nullable=True)
    current_week = Column(Integer, default=1)
    completed_weeks = Column(JSON, default=list)  # List of week numbers
    mentor_id = Column(String, ForeignKey("users.id"), nullable=True)
    parent_email = Column(String, nullable=True)
    parent_name = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)

    # Mentor specific fields
    membership_number = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    assigned_mentees = Column(JSON, default=list)  # List of mentee IDs

    # Parent specific fields
    phone = Column(String, nullable=True)
    children = Column(JSON, default=list)  # List of mentee IDs

    # Relationships
    mentor = relationship("User", remote_side=[id], foreign_keys=[mentor_id])
    sent_messages = relationship("Message", foreign_keys="Message.from_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.to_id", back_populates="recipient")
    week_approvals = relationship("WeekApproval", foreign_keys="WeekApproval.mentee_id", back_populates="mentee")
    mentor_approvals = relationship("WeekApproval", foreign_keys="WeekApproval.mentor_id", back_populates="mentor")


class WeekActivity(Base):
    __tablename__ = "week_activities"

    week = Column(Integer, primary_key=True, index=True)
    bloc_number = Column(Integer, nullable=False)
    sub_theme = Column(String, nullable=False)
    activity_name = Column(String, nullable=False)
    learning_outcome = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    digitization = Column(Text, nullable=False)
    talent_indicators = Column(JSON, nullable=False)  # List of strings


class WeekApproval(Base):
    __tablename__ = "week_approvals"

    id = Column(String, primary_key=True, index=True)
    mentee_id = Column(String, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    mentor_id = Column(String, ForeignKey("users.id"), nullable=False)
    mentor_feedback = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    mentee_comment = Column(Text, nullable=True)
    mentee_comment_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    mentee = relationship("User", foreign_keys=[mentee_id], back_populates="week_approvals")
    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="mentor_approvals")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    from_id = Column(String, ForeignKey("users.id"), nullable=False)
    to_id = Column(String, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # parent_to_mentor, mentor_to_parent, admin_to_*, etc.
    status = Column(String, default="awaiting_response")  # awaiting_response, responded, sent
    week_number = Column(Integer, nullable=True)
    parent_message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    response = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sender = relationship("User", foreign_keys=[from_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[to_id], back_populates="received_messages")
    parent_message = relationship("Message", remote_side=[id], foreign_keys=[parent_message_id])


class AdminReview(Base):
    __tablename__ = "admin_reviews"

    id = Column(String, primary_key=True, index=True)
    mentee_id = Column(String, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(String, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MentorFeedback(Base):
    __tablename__ = "mentor_feedbacks"

    id = Column(String, primary_key=True, index=True)
    mentee_id = Column(String, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(String, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

