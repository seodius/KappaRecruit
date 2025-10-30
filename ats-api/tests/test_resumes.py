import io
import json
import pytest

# A fixture to create a common job payload
@pytest.fixture
def job_payload():
    return {
        "jobId": "test-engineer-123",
        "descriptions": [{"text": "A job for testing."}],
        "company_id": 1,
        "location": {"type": "Onsite"},
        "employmentType": "Full-time",
        "responsibilities": ["Write tests"],
    }

# A fixture to create a common resume payload
@pytest.fixture
def resume_payload(candidate_id_fixture):
    return {
        "candidate_id": candidate_id_fixture,
        "basics": {"name": "John Doe", "email": "john.doe@example.com"},
        "work": [],
        "education": [],
    }

# A fixture that creates a candidate and returns its ID
@pytest.fixture
def candidate_id_fixture(client, auth_token_company_1):
    response = client.post(
        "/api/v1/candidates",
        json={"email": "test.candidate@example.com"},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert response.status_code == 200
    return response.json()["candidate_id"]

def test_create_resume_with_upload(client, auth_token_company_1, job_payload, resume_payload):
    # Create a job first
    job_response = client.post(
        "/api/v1/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["job_id"]

    # Create an application to link the candidate to the company
    app_response = client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": resume_payload["candidate_id"]},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert app_response.status_code == 200

    # Create the resume
    resume_file = ("test_resume.pdf", io.BytesIO(b"test resume content"), "application/pdf")
    response = client.post(
        "/api/v1/resumes",
        data={"resume_data": json.dumps(resume_payload)},
        files={"file": resume_file},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )

    assert response.status_code == 200
    resume_id = response.json()["resume_id"]
    assert response.json()["basics"]["name"] == "John Doe"
    file_location = response.json()["file_location"]
    assert file_location.startswith("uploads/")
    assert file_location.endswith(".pdf")

    # Verify GET request for the created resume
    get_res = client.get(
        f"/api/v1/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["resume_id"] == resume_id
    assert get_res.json()["basics"]["name"] == "John Doe"

def test_multi_tenancy_resume_access_is_isolated(client, auth_token_company_1, auth_token_company_2, job_payload, resume_payload):
    # Company 1 creates a job
    job_response = client.post(
        "/api/v1/jobs",
        json=job_payload,
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["job_id"]

    # Company 1 creates an application for the candidate
    app_response = client.post(
        "/api/v1/applications",
        json={"job_id": job_id, "candidate_id": resume_payload["candidate_id"]},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert app_response.status_code == 200

    # Company 1 creates a resume for the candidate
    resume_file = ("test_resume.pdf", io.BytesIO(b"test resume content"), "application/pdf")
    resume_response = client.post(
        "/api/v1/resumes",
        data={"resume_data": json.dumps(resume_payload)},
        files={"file": resume_file},
        headers={"Authorization": f"Bearer {auth_token_company_1}"}
    )
    assert resume_response.status_code == 200
    resume_id = resume_response.json()["resume_id"]

    # Company 2 attempts to access the resume created by Company 1
    response = client.get(
        f"/api/v1/resumes/{resume_id}",
        headers={"Authorization": f"Bearer {auth_token_company_2}"}
    )

    assert response.status_code == 404
