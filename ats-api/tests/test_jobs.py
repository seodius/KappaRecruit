import pytest
from uuid import uuid4

def test_job_workflow_and_security(client, auth_token_company_1, auth_token_company_2):
    # 1. Test Job Creation
    job_payload = {
        "jobId": str(uuid4()),
        "description": "A job for workflow testing.",
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
    assert create_res.json()["description"] == "A job for workflow testing."

    # 1a. Verify GET request for the created job
    get_res = client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["job_id"] == job_id
    assert get_res.json()["company"]["name"] == "Test Company" # From seed_db

    # 2. Test Missing Field Validation
    invalid_payload = job_payload.copy()
    del invalid_payload["description"]
    invalid_res = client.post(
        "/api/v1/jobs",
        json=invalid_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert invalid_res.status_code == 422

    # 3. Test Multi-Tenancy Security
    # Client from Company 2 should NOT be able to access the job.
    unauthorized_res = client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {auth_token_company_2}"}
    )
    assert unauthorized_res.status_code == 404
