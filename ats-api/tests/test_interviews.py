import pytest
from datetime import datetime, timezone

def test_interview_and_evaluation_workflow(client, auth_token_company_1):
    # Setup: Create a job, candidate, and application
    job_payload = {
        "jobId": "interview-test-job-123",
        "description": "A job for interview testing.",
        "company_id": 1,
        "company": {"name": "Interview Test Corp"},
        "location": {"type": "Hybrid"},
        "employmentType": "Full-time",
        "responsibilities": ["Being interviewed"],
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
        json={"email": "interview.candidate@test.com"},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert cand_res.status_code == 200
    candidate_id = cand_res.json()["candidate_id"]

    app_res = client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": candidate_id},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert app_res.status_code == 200
    application_id = app_res.json()["application_id"]

    # 1. Test Interview Creation
    interview_payload = {
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
        "duration_minutes": 45,
        "interview_type": "video",
        "interviewers": [{"user_id": 1}]  # Assumes a user with ID 1 exists
    }
    interview_res = client.post(
        f"/api/v1/applications/{application_id}/interviews",
        json=interview_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert interview_res.status_code == 200
    interview_id = interview_res.json()["interview_id"]
    assert interview_res.json()["duration_minutes"] == 45
    assert len(interview_res.json()["interviewers"]) > 0

    # 2. Test Evaluation Creation for that Interview
    evaluation_payload = {
        "rating": 5,
        "feedback": "The candidate was exceptional.",
        "interviewer_id": 1 # In a real system, this would be the user_id of the interviewer
    }
    eval_res = client.post(
        f"/api/v1/interviews/{interview_id}/evaluations",
        json=evaluation_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert eval_res.status_code == 200
    assert eval_res.json()["rating"] == 5
    assert eval_res.json()["feedback"] == "The candidate was exceptional."
