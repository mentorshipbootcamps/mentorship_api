import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Curriculum Development API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_register_user():
    """Test user registration"""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {
        "name": "Test User",
        "email": unique_email,
        "password": "testpassword123",
        "role": "mentee"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "mentee"
    assert data["user"]["mentee_number"] is not None


def test_register_duplicate_email():
    """Test registration with duplicate email"""
    register_data = {
        "name": "Test User 2",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "mentee"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_role():
    """Test registration with invalid role"""
    register_data = {
        "name": "Test User",
        "email": "test2@example.com",
        "password": "testpassword123",
        "role": "invalid_role"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 400


def test_login():
    """Test user login"""
    login_data = {
        "email": "admin@gmail.com",
        "password": "admin@gmail.com"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "admin@gmail.com"
    assert data["user"]["role"] == "admin"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    login_data = {
        "email": "admin@gmail.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401


def test_register_mentor():
    """Test mentor registration"""
    unique_email = f"mentor_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {
        "name": "Test Mentor",
        "email": unique_email,
        "password": "mentorpass123",
        "role": "mentor",
        "specialization": "Mathematics",
        "bio": "Experienced math teacher"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "mentor"
    assert data["user"]["membership_number"] is not None
    assert data["user"]["specialization"] == "Mathematics"


def test_register_parent():
    """Test parent registration"""
    unique_email = f"parent_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {
        "name": "Test Parent",
        "email": unique_email,
        "password": "parentpass123",
        "role": "parent",
        "phone": "+1234567890"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "parent"
    assert data["user"]["phone"] == "+1234567890"

