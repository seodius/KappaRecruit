"""
Tests for the candidate portal endpoints (`/me/`).
"""

import pytest
from fastapi.testclient import TestClient
from app import models

@pytest.fixture
def candidate_token(client, db, admin_token):
    """
    Registers a new candidate and returns an authentication token.
    """
    # Use the admin token to create the "Candidate" role
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_payload = {"name": "Candidate", "permissions": []}
    role_res = client.post("/api/v1/roles", json=role_payload, headers=headers)
    assert role_res.status_code == 200
    candidate_role_id = role_res.json()["role_id"]

    # Register and log in the candidate
    user_payload = {
        "email": "candidate_me@test.com",
        "password": "password",
        "first_name": "Candidate",
        "last_name": "User",
        "role_id": candidate_role_id,
        "company_id": None
    }
    register_res = client.post("/api/v1/auth/candidate/register", json=user_payload)
    assert register_res.status_code == 200
    return register_res.json()["access_token"]

def test_candidate_can_access_own_profile(client, candidate_token):
    """
    Tests that a logged-in candidate can access their own profile.
    """
    headers = {"Authorization": f"Bearer {candidate_token}"}
    response = client.get("/api/v1/me/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "candidate_me@test.com"

def test_regular_user_cannot_access_me_endpoints(client, auth_token_company_1):
    """
    Tests that a regular user (e.g., a recruiter) cannot access the candidate-specific endpoints.
    """
    headers = {"Authorization": f"Bearer {auth_token_company_1}"}
    response = client.get("/api/v1/me/profile", headers=headers)
    assert response.status_code == 403
