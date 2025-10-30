import pytest

def test_candidate_workflow_and_security(client, auth_token_company_1, auth_token_company_2):
    # 1. Test Candidate Creation
    candidate_payload = {
        "email": "candidate.workflow@test.com",
        "first_name": "Workflow",
        "last_name": "Candidate",
        "job_title": "Tester",
    }
    create_res = client.post(
        "/api/v1/candidates",
        json=candidate_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert create_res.status_code == 200
    candidate_id = create_res.json()["candidate_id"]
    assert create_res.json()["email"] == "candidate.workflow@test.com"
    assert create_res.json()["job_title"] == "Tester"

    # To make this candidate accessible for testing, we need to associate them
    # with Company 1 via an application.
    job_payload = {
        "jobId": "cand-sec-job-123",
            "descriptions": [{"text": "A job for security testing."}],
        "company_id": 1,
        "location": {"type": "Onsite"},
        "employmentType": "Contract",
        "responsibilities": ["Security checks"],
    }
    job_res = client.post(
        "/api/v1/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert job_res.status_code == 200
    job_id = job_res.json()["job_id"]

    app_payload = {"job_id": job_id, "candidate_id": candidate_id}
    app_res = client.post(
        "/api/v1/applications",
        json=app_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert app_res.status_code == 200

    # 2. Test Multi-Tenancy Security
    # Client from Company 2 should NOT be able to access the candidate.
    unauthorized_res = client.get(
        f"/api/v1/candidates/{candidate_id}",
        headers={"Authorization": f"Bearer {auth_token_company_2}"}
    )
    assert unauthorized_res.status_code == 404

    # 3. Test Duplicate Candidate Creation
    # The API should not create a new candidate with the same email, but return the existing one.
    duplicate_res = client.post(
        "/api/v1/candidates",
        json=candidate_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert duplicate_res.status_code == 200
    assert duplicate_res.json()["candidate_id"] == candidate_id
