from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.curriculum.router import router as curriculum_router
from app.approvals.router import router as approvals_router
from app.messages.router import router as messages_router
from app.notifications.router import router as notifications_router
from app.analytics.router import router as analytics_router

# Note: Database tables are created in Supabase
# Run supabase_schema.sql in Supabase SQL Editor to create tables

app = FastAPI(
    title="Curriculum Development API",
    description="Backend API for Curriculum Development Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(curriculum_router)
app.include_router(approvals_router)
app.include_router(messages_router)
app.include_router(notifications_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    return {
        "message": "Curriculum Development API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
