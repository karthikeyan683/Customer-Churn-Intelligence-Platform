
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


def test_single_prediction(client):
    token = get_admin_token(client)

    response = client.post(
        "/predictions/CUS-0001",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "customer_id" in data
    assert "churn_probability" in data
    assert "risk_level" in data

    assert data["customer_id"] == "CUS-0001"

    assert data["risk_level"] in [
        "Low",
        "Medium",
        "High"
    ]

    assert 0 <= data["churn_probability"] <= 100


def test_batch_prediction(client):
    token = get_admin_token(client)

    response = client.post(
        "/predictions/batch",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_predictions" in data
    assert "predictions" in data

    assert data["total_predictions"] > 0
    assert len(data["predictions"]) > 0

    prediction = data["predictions"][0]

    assert "customer_id" in prediction
    assert "customer_name" in prediction
    assert "churn_probability" in prediction
    assert "risk_level" in prediction


def test_prediction_history(client):
    token = get_admin_token(client)

    response = client.get(
        "/predictions/CUS-0001/history",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data) > 0:
        prediction = data[0]

        assert "churn_probability" in prediction
        assert "risk_level" in prediction
        assert "model_version" in prediction


def test_prediction_explanation(client):
    token = get_admin_token(client)

    response = client.post(
        "/predictions/CUS-0001/explain",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "customer_id" in data
    assert "explanations" in data

    assert data["customer_id"] == "CUS-0001"

    explanations = data["explanations"]

    assert isinstance(explanations, list)

    assert len(explanations) > 0

    feature = explanations[0]

    assert "feature" in feature
    assert "impact" in feature
    assert "direction" in feature


def test_prediction_customer_not_found(client):
    token = get_admin_token(client)

    response = client.post(
        "/predictions/CUS-9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_prediction_without_token(client):
    response = client.post(
        "/predictions/CUS-0001"
    )

    assert response.status_code == 401
