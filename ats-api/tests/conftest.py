import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def seed_db(db):
    company1 = models.Company(name="Test Company", company_id=1)
    company2 = models.Company(name="Second Company", company_id=2)
    role = models.Role(name="Test Role", role_id=1)
    db.add(company1)
    db.add(company2)
    db.add(role)
    db.commit()

@pytest.fixture(scope="function")
def auth_token_company_1(client, seed_db):
    client.post("/api/v1/auth/register", json={"email": "test@test.com", "password": "password", "company_id": 1, "role_id": 1})
    login_response = client.post("/api/v1/auth/login", data={"username": "test@test.com", "password": "password"})
    return login_response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_token_company_2(client, seed_db):
    client.post("/api/v1/auth/register", json={"email": "test2@test.com", "password": "password", "company_id": 2, "role_id": 1})
    login_response = client.post("/api/v1/auth/login", data={"username": "test2@test.com", "password": "password"})
    return login_response.json()["access_token"]
