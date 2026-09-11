from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app)

TEST_EMAIL = "pytest_user2@example.com"
TEST_PASSWORD = "test123"


def get_customer_token():
    response = client.post(
        "/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def get_admin_token():
    response = client.post(
        "/auth/login",
        json={
            "email": settings.test_admin_email,
            "password": settings.test_admin_password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_order():
    token = get_customer_token()

    response = client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
            "shipping_address": {
                "city": "Kolkata",
                "state": "West Bengal",
                "pincode": "700001",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "total" in data
    assert data["status"] == "pending"

    # Product 1 price comes from the database.
    # ₹85,000 × 1 = ₹85,000
    assert float(data["total"]) == 85000.00


def test_get_my_orders():
    token = get_customer_token()

    response = client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0


def test_customer_cannot_access_another_customers_order():
    token = get_customer_token()

    response = client.get(
        "/orders/4",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_invalid_order_status_transition():
    token = get_admin_token()

    response = client.put(
        "/orders/1/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "pending"},
    )

    assert response.status_code == 400