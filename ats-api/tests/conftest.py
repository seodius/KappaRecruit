"""
Pytest fixtures for the ATS API test suite.

This file defines reusable components for testing, such as database sessions,
API clients, and pre-populated data.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Use an in-memory SQLite database for testing to ensure isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Provides a clean, isolated database session for each test function.
    It creates all tables before the test and drops them afterward.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Provides a TestClient for making API requests to the application.
    It overrides the `get_db` dependency to use the isolated test database.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def seed_db(db):
    """
    Seeds the database with initial data required for multi-tenancy tests,
    including two distinct companies and a default user role.
    """
    company1 = models.Company(name="Test Company", company_id=1)
    company2 = models.Company(name="Second Company", company_id=2)
    role = models.Role(name="Test Role", role_id=1)
    candidate_role = models.Role(name="Candidate", role_id=2)
    db.add(company1)
    db.add(company2)
    db.add(role)
    db.add(candidate_role)
    db.commit()

@pytest.fixture(scope="function")
def auth_token_company_1(client, seed_db):
    """
    Registers and logs in a user for Company 1, returning a JWT access token.
    """
    client.post("/api/v1/auth/register", json={"email": "test@test.com", "password": "password", "company_id": 1, "role_id": 1})
    login_response = client.post("/api/v1/auth/login", data={"username": "test@test.com", "password": "password"})
    return login_response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_token_company_2(client, seed_db):
    """
    Registers and logs in a user for Company 2, returning a JWT access token.
    This is used for testing multi-tenancy data isolation.
    """
    client.post("/api/v1/auth/register", json={"email": "test2@test.com", "password": "password", "company_id": 2, "role_id": 1})
    login_response = client.post("/api/v1/auth/login", data={"username": "test2@test.com", "password": "password"})
    return login_response.json()["access_token"]

@pytest.fixture(scope="function")
def admin_token(client, db):
    """
    Creates an Administrator role and user, then returns a JWT access token for that user.
    """
    # Create the Administrator role
    admin_role = models.Role(name="Administrator", permissions=["manage_roles"])
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

    # Create the admin user
    client.post("/api/v1/auth/register", json={"email": "admin@test.com", "password": "password", "company_id": 1, "role_id": admin_role.role_id})
    login_response = client.post("/api/v1/auth/login", data={"username": "admin@test.com", "password": "password"})
    return login_response.json()["access_token"]
