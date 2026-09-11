from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TEST_EMAIL = "pytest_user2@example.com"
TEST_PASSWORD = "test123"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    # User may already exist from an earlier test run.
    if response.status_code == 400:
        assert response.json()["detail"] == "Email already registered"
        return

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == TEST_EMAIL
    assert "id" in data


def test_login_user():
    response = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_me():
    login_response = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == TEST_EMAIL
    assert "id" in data
    assert "role" in data