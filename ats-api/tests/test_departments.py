"""
Tests for the department management workflow.
"""

import pytest
from fastapi.testclient import TestClient

def test_department_workflow(client, auth_token_company_1):
    """
    Tests the complete lifecycle of a department.
    """
    headers = {"Authorization": f"Bearer {auth_token_company_1}"}

    # --- 1. Test Department Creation ---
    department_payload = {
        "name": "Engineering",
        "company_id": 1
    }
    create_res = client.post("/api/v1/companies/1/departments", json=department_payload, headers=headers)
    assert create_res.status_code == 200
    department_id = create_res.json()["department_id"]
    assert create_res.json()["name"] == "Engineering"

    # --- 2. Test Hierarchical Department Creation ---
    child_department_payload = {
        "name": "Backend",
        "company_id": 1,
        "parent_department_id": department_id
    }
    child_create_res = client.post("/api/v1/companies/1/departments", json=child_department_payload, headers=headers)
    assert child_create_res.status_code == 200
    child_department_id = child_create_res.json()["department_id"]
    assert child_create_res.json()["name"] == "Backend"
    assert child_create_res.json()["parent_department_id"] == department_id

    # --- 3. Test Department Retrieval ---
    read_res = client.get(f"/api/v1/departments/{department_id}", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["name"] == "Engineering"
    assert len(read_res.json()["children"]) == 1
    assert read_res.json()["children"][0]["name"] == "Backend"

    # --- 4. Test Department Update ---
    update_payload = {"name": "Software Engineering"}
    update_res = client.put(f"/api/v1/departments/{department_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Software Engineering"

    # --- 5. Test Department Deletion ---
    delete_res = client.delete(f"/api/v1/departments/{department_id}", headers=headers)
    assert delete_res.status_code == 200
