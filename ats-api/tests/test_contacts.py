"""
Tests for the contact management workflow.
"""

import pytest
from fastapi.testclient import TestClient

def test_contact_workflow(client, auth_token_company_1):
    """
    Tests the complete lifecycle of a contact.
    """
    headers = {"Authorization": f"Bearer {auth_token_company_1}"}

    # --- 1. Test Contact Creation for a Company ---
    contact_payload = {
        "name": "John Doe",
        "email": "john.doe@test.com",
        "phone": "123-456-7890",
        "company_id": 1
    }
    create_res = client.post("/api/v1/contacts", json=contact_payload, headers=headers)
    assert create_res.status_code == 200
    contact_id = create_res.json()["contact_id"]
    assert create_res.json()["name"] == "John Doe"
    assert create_res.json()["company_id"] == 1

    # --- 2. Test Contact Retrieval ---
    read_res = client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["name"] == "John Doe"

    # --- 3. Test Contact Update ---
    update_payload = {"name": "Johnathan Doe"}
    update_res = client.put(f"/api/v1/contacts/{contact_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Johnathan Doe"

    # --- 4. Test Contact Deletion ---
    delete_res = client.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert delete_res.status_code == 200
