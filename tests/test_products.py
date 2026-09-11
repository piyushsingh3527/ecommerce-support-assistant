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


def test_get_products():
    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_create_product_as_admin():
    token = get_admin_token()

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/products/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "category_id": 1,
            "sku": f"TEST-SKU-{unique_id}",
            "name": f"Test Laptop {unique_id}",
            "price": 50000,
            "stock": 10,
            "specifications": {
                "brand": "Test Brand",
                "ram": "16GB",
                "storage": "512GB SSD"
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sku"].startswith("TEST-SKU-")
    assert data["name"].startswith("Test Laptop")
    assert float(data["price"]) == 50000
    assert data["stock"] == 10
    assert data["specifications"]["ram"] == "16GB"
    assert "id" in data