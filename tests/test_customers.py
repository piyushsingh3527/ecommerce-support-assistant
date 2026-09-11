from fastapi.testclient import TestClient

from app.main import app


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


def test_create_customer_profile():
    token = get_customer_token()

    response = client.post(
        "/customers/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "phone": "9876543210",
            "address": {
                "city": "Kolkata",
                "state": "West Bengal",
                "pincode": "700001",
            },
        },
    )

    # Profile may already exist from a previous test/manual test.
    assert response.status_code in [200, 400]

    if response.status_code == 200:
        data = response.json()

        assert data["phone"] == "9876543210"
        assert data["address"]["city"] == "Kolkata"


def test_get_my_customer_profile():
    token = get_customer_token()

    response = client.get(
        "/customers/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "user_id" in data
    assert "phone" in data
    assert "address" in data