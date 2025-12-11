-- Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create all required tables
-- Go to: https://app.supabase.com/project/xlkqhnssdyfxqjvtyxcp/sql/new

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    profile_picture TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Mentee specific fields
    mentee_number TEXT,
    current_week INTEGER DEFAULT 1,
    completed_weeks JSONB DEFAULT '[]'::jsonb,
    mentor_id TEXT REFERENCES users(id),
    parent_email TEXT,
    parent_name TEXT,
    parent_phone TEXT,
    
    -- Mentor specific fields
    membership_number TEXT,
    specialization TEXT,
    bio TEXT,
    assigned_mentees JSONB DEFAULT '[]'::jsonb,
    
    -- Parent specific fields
    phone TEXT,
    children JSONB DEFAULT '[]'::jsonb
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_mentor_id ON users(mentor_id);

-- Week Activities table
CREATE TABLE IF NOT EXISTS week_activities (
    week INTEGER PRIMARY KEY,
    bloc_number INTEGER NOT NULL,
    sub_theme TEXT NOT NULL,
    activity_name TEXT NOT NULL,
    learning_outcome TEXT NOT NULL,
    description TEXT NOT NULL,
    digitization TEXT NOT NULL,
    talent_indicators JSONB NOT NULL
);

-- Week Approvals table
CREATE TABLE IF NOT EXISTS week_approvals (
    id TEXT PRIMARY KEY,
    mentee_id TEXT NOT NULL REFERENCES users(id),
    week_number INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    mentor_id TEXT NOT NULL REFERENCES users(id),
    mentor_feedback TEXT,
    approved_at TIMESTAMPTZ,
    mentee_comment TEXT,
    mentee_comment_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_week_approvals_mentee_id ON week_approvals(mentee_id);
CREATE INDEX IF NOT EXISTS idx_week_approvals_mentor_id ON week_approvals(mentor_id);
CREATE INDEX IF NOT EXISTS idx_week_approvals_status ON week_approvals(status);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    from_id TEXT NOT NULL REFERENCES users(id),
    to_id TEXT NOT NULL REFERENCES users(id),
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'awaiting_response',
    week_number INTEGER,
    parent_message_id TEXT REFERENCES messages(id),
    response TEXT,
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_from_id ON messages(from_id);
CREATE INDEX IF NOT EXISTS idx_messages_to_id ON messages(to_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent_message_id ON messages(parent_message_id);

-- Admin Reviews table
CREATE TABLE IF NOT EXISTS admin_reviews (
    id TEXT PRIMARY KEY,
    mentee_id TEXT NOT NULL REFERENCES users(id),
    reviewer_id TEXT NOT NULL REFERENCES users(id),
    week_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_reviews_mentee_id ON admin_reviews(mentee_id);
CREATE INDEX IF NOT EXISTS idx_admin_reviews_reviewer_id ON admin_reviews(reviewer_id);

-- Mentor Feedbacks table
CREATE TABLE IF NOT EXISTS mentor_feedbacks (
    id TEXT PRIMARY KEY,
    mentee_id TEXT NOT NULL REFERENCES users(id),
    mentor_id TEXT NOT NULL REFERENCES users(id),
    week_number INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mentor_feedbacks_mentee_id ON mentor_feedbacks(mentee_id);
CREATE INDEX IF NOT EXISTS idx_mentor_feedbacks_mentor_id ON mentor_feedbacks(mentor_id);

-- Enable Row Level Security (optional, for additional security)
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE week_approvals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

