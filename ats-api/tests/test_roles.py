"""
Tests for the role management and RBAC functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app import models

@pytest.fixture(scope="function")
def regular_user_token(client, db, admin_token):
    """
    Creates a regular user with no special permissions and returns an authentication token.
    """
    # Use the admin token to create a new role for the regular user
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_payload = {"name": "Recruiter", "permissions": []}
    role_res = client.post("/api/v1/roles", json=role_payload, headers=headers)
    assert role_res.status_code == 200
    regular_role_id = role_res.json()["role_id"]

    # Register and log in the new user
    client.post("/api/v1/auth/register", json={"email": "user@test.com", "password": "password", "company_id": 1, "role_id": regular_role_id})
    login_res = client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "password"})
    return login_res.json()["access_token"]


def test_admin_can_manage_roles(client, admin_token):
    """
    Tests that an administrator can create, read, update, and delete roles.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a new role
    new_role_payload = {"name": "Hiring Manager", "permissions": ["view_candidates"]}
    create_res = client.post("/api/v1/roles", json=new_role_payload, headers=headers)
    assert create_res.status_code == 200
    role_id = create_res.json()["role_id"]
    assert create_res.json()["name"] == "Hiring Manager"

    # Read the new role
    read_res = client.get(f"/api/v1/roles/{role_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["name"] == "Hiring Manager"

    # Update the new role
    update_payload = {"name": "Senior Hiring Manager", "permissions": ["view_candidates", "create_offer"]}
    update_res = client.put(f"/api/v1/roles/{role_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Senior Hiring Manager"

    # Delete the new role
    delete_res = client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert delete_res.status_code == 200

def test_regular_user_cannot_manage_roles(client, regular_user_token):
    """
    Tests that a regular user cannot access the role management endpoints.
    """
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    new_role_payload = {"name": "Forbidden Role", "permissions": []}

    # Attempt to create a role
    create_res = client.post("/api/v1/roles", json=new_role_payload, headers=headers)
    assert create_res.status_code == 403

    # Attempt to read roles
    read_res = client.get("/api/v1/roles", headers=headers)
    assert read_res.status_code == 403
