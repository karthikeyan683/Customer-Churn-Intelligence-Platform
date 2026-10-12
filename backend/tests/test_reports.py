
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


def test_churn_summary_report(client):
    token = get_admin_token(client)

    response = client.get(
        "/reports/churn-summary",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, (dict, list))


def test_customer_risk_report(client):
    token = get_admin_token(client)

    response = client.get(
        "/reports/customer-risk",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, (dict, list))


def test_revenue_risk_report(client):
    token = get_admin_token(client)

    response = client.get(
        "/reports/revenue-risk",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, (dict, list))


def test_export_report(client):
    token = get_admin_token(client)

    response = client.get(
        "/reports/export",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    content_type = response.headers.get(
        "content-type",
        ""
    )

    assert "text/csv" in content_type

    assert len(response.content) > 0


def test_reports_without_token(client):
    response = client.get(
        "/reports/churn-summary"
    )

    assert response.status_code == 401
