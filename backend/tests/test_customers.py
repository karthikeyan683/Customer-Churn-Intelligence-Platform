
import uuid


def get_admin_token(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@churnintel.com",
            "password": "Admin@12345"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_customer(client):
    token = get_admin_token(client)

    unique_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
    unique_email = f"{uuid.uuid4().hex[:8]}@example.com"

    customer_data = {
        "customer_id": unique_id,
        "full_name": "Test Customer",
        "email": unique_email,
        "gender": "Male",
        "age": 30,
        "tenure_months": 12,
        "monthly_charges": 50.0,
        "total_charges": 600.0,
        "contract_type": "One year",
        "payment_method": "Credit card",
        "internet_service": "DSL",
        "support_tickets": 1,
        "satisfaction_score": 8.0,
        "churned": False
    }

    response = client.post(
        "/customers/",
        json=customer_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == unique_id
    assert data["full_name"] == "Test Customer"
    assert data["email"] == unique_email


def test_get_customers(client):
    token = get_admin_token(client)

    response = client.get(
        "/customers/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    assert "customer_id" in data[0]
    assert "full_name" in data[0]
    assert "email" in data[0]


def test_get_single_customer(client):
    token = get_admin_token(client)

    response = client.get(
        "/customers/CUS-0001",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == "CUS-0001"


def test_customer_not_found(client):
    token = get_admin_token(client)

    response = client.get(
        "/customers/CUS-9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_customer_without_token(client):
    response = client.get(
        "/customers/CUS-0001"
    )

    assert response.status_code == 401
