import pytest

def test_application_workflow_and_security(client, auth_token_company_1, auth_token_company_2):
    # Setup: Create a job and a candidate for Company 1
    job_payload = {
        "jobId": "app-test-job-123",
        "descriptions": [{"text": "A job for application testing."}],
        "company_id": 1,
        "location": {"type": "Remote"},
        "employmentType": "Full-time",
        "responsibilities": ["Testing applications"],
    }
    job_res = client.post(
        "/api/v1/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert job_res.status_code == 200
    job_id = job_res.json()["job_id"]

    cand_res = client.post(
        "/api/v1/candidates",
        json={"email": "application.candidate@test.com"},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert cand_res.status_code == 200
    candidate_id = cand_res.json()["candidate_id"]

    # 1. Test Application Creation
    app_payload = {"job_id": job_id, "candidate_id": candidate_id}
    app_res = client.post(
        "/api/v1/applications",
        json=app_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert app_res.status_code == 200
    application_id = app_res.json()["application_id"]
    assert app_res.json()["job_id"] == job_id
    assert app_res.json()["candidate_id"] == candidate_id

    # 2. Test Application Status Update
    status_event_payload = {
        "status": "screening",
        "changed_by_user_id": 1  # In a real app, this would come from the token
    }
    status_res = client.post(
        f"/api/v1/applications/{application_id}/status",
        json=status_event_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "screening"

    # 3. Test Multi-Tenancy Security
    # Client from Company 2 should NOT be able to access the application.
    unauthorized_res = client.get(
        f"/api/v1/applications/{application_id}",
        headers={"Authorization": f"Bearer {auth_token_company_2}"}
    )
    assert unauthorized_res.status_code == 404
