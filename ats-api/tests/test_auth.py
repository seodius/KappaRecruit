def test_register_user(client, seed_db):
    response = client.post("/api/v1/auth/register", json={"email": "test@test.com", "password": "password", "company_id": 1, "role_id": 1})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user(client, seed_db):
    client.post("/api/v1/auth/register", json={"email": "test2@test.com", "password": "password", "company_id": 1, "role_id": 1})
    response = client.post("/api/v1/auth/login", data={"username": "test2@test.com", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
