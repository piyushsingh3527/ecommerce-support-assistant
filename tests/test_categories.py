from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def get_admin_token():
    assert settings.test_admin_email, "TEST_ADMIN_EMAIL is not configured in .env"
    assert settings.test_admin_password, "TEST_ADMIN_PASSWORD is not configured in .env"

    response = client.post(
        "/auth/login",
        json={
            "email": settings.test_admin_email,
            "password": settings.test_admin_password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_get_categories():
    response = client.get("/categories/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_create_category_as_admin():
    token = get_admin_token()

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/categories/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": f"Test Electronics {unique_id}",
            "slug": f"test-electronics-{unique_id}",
            "description": "Category created by automated test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"].startswith("Test Electronics")
    assert data["slug"].startswith("test-electronics")
    assert "id" in data


def test_customer_cannot_create_category():
    response = client.post(
        "/auth/login",
        json={
            "email": "pytest_user2@example.com",
            "password": "test123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.post(
        "/categories/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Unauthorized Category",
            "slug": "unauthorized-category",
            "description": "This should not be created",
        },
    )

    assert response.status_code == 403