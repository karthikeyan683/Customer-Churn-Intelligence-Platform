
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


def test_analytics_summary(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/summary",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_churn_by_contract(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/churn-by-contract",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data) > 0:
        item = data[0]

        assert isinstance(item, dict)


def test_risk_distribution(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/risk-distribution",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data) > 0:
        item = data[0]

        assert "risk_level" in item
        assert "customer_count" in item


def test_high_risk_customers(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/high-risk-customers",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_at_risk_customers(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/at-risk-customers",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_revenue_at_risk(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/revenue-at-risk",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_risk_segments(client):
    token = get_admin_token(client)

    response = client.get(
        "/analytics/risk-segments",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data) > 0:
        segment = data[0]

        assert "risk_level" in segment
        assert "customer_count" in segment
        assert "monthly_revenue" in segment


def test_analytics_without_token(client):
    response = client.get(
        "/analytics/summary"
    )

    assert response.status_code == 401
