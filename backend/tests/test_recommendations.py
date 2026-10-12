
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


def test_customer_recommendations(client):
    token = get_admin_token(client)

    response = client.post(
        "/recommendations/CUS-0001",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "customer_id" in data
    assert "customer_name" in data
    assert "churn_probability" in data
    assert "risk_level" in data
    assert "recommendations" in data

    assert data["customer_id"] == "CUS-0001"

    assert data["risk_level"] in [
        "Low",
        "Medium",
        "High"
    ]

    assert isinstance(data["recommendations"], list)


def test_recommendations_have_required_fields(client):
    token = get_admin_token(client)

    response = client.post(
        "/recommendations/CUS-0001",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    assert len(recommendations) > 0

    recommendation = recommendations[0]

    assert "priority" in recommendation
    assert "category" in recommendation
    assert "action" in recommendation


def test_recommendation_customer_not_found(client):
    token = get_admin_token(client)

    response = client.post(
        "/recommendations/CUS-9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_recommendations_without_token(client):
    response = client.post(
        "/recommendations/CUS-0001"
    )

    assert response.status_code == 401


def test_recommendation_risk_level(client):
    token = get_admin_token(client)

    response = client.post(
        "/recommendations/CUS-0010",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] in [
        "Low",
        "Medium",
        "High"
    ]

    assert 0 <= data["churn_probability"] <= 100
