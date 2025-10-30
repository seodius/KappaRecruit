"""
Tests for the job management workflow, including creation, retrieval,
validation, and multi-tenant security.
"""

import pytest
from uuid import uuid4

def test_job_workflow_and_security(client, auth_token_company_1, auth_token_company_2):
    """
    Tests the complete lifecycle and security of a job posting.
    """
    # --- 1. Test Job Creation ---
    job_payload = {
        "jobId": str(uuid4()),
        "descriptions": [
            {
                "text": "A job for workflow testing.",
                "goal": "Internal testing",
                "target_platform": "Web",
                "language": "en-US"
            }
        ],
        "company_id": 1,
        "location": {"type": "Onsite"},
        "employmentType": "Full-time",
        "responsibilities": ["Participating in tests"],
    }
    create_res = client.post(
        "/api/v1/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert create_res.status_code == 200
    job_id = create_res.json()["job_id"]
    assert create_res.json()["descriptions"][0]["text"] == "A job for workflow testing."

    # --- 1a. Verify Retrieval of the Created Job ---
    get_res = client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["job_id"] == job_id
    assert get_res.json()["company"]["name"] == "Test Company"  # From seed_db in conftest.py
    assert len(get_res.json()["descriptions"]) == 1

    # --- 2. Test Input Validation (Missing Field) ---
    invalid_payload = job_payload.copy()
    del invalid_payload["descriptions"]
    invalid_res = client.post(
        "/api/v1/jobs",
        json=invalid_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert invalid_res.status_code == 422  # Unprocessable Entity for validation errors

    # --- 3. Test Multi-Tenancy Security ---
    # A client authenticated for Company 2 should NOT be able to access the job
    # created by Company 1. This verifies data isolation.
    unauthorized_res = client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {auth_token_company_2}"}
    )
    assert unauthorized_res.status_code == 404  # Not Found, as the job is outside their scope
