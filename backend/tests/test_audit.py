
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


def get_analyst_token(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "audit_analyst@test.com",
            "full_name": "Audit Analyst",
            "password": "Analyst@12345",
            "role": "analyst"
        }
    )

    # If the user already exists, login instead.
    if response.status_code == 400:
        response = client.post(
            "/auth/login",
            json={
                "email": "audit_analyst@test.com",
                "password": "Analyst@12345"
            }
        )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_admin_can_access_audit_logs(client):
    token = get_admin_token(client)

    response = client.get(
        "/audit/logs",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_audit_logs_contain_expected_fields(client):
    token = get_admin_token(client)

    response = client.get(
        "/audit/logs",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    if len(data) > 0:
        log = data[0]

        assert "id" in log
        assert "user_id" in log
        assert "action" in log
        assert "endpoint" in log
        assert "status" in log
        assert "created_at" in log


def test_analyst_cannot_access_audit_logs(client):
    token = get_analyst_token(client)

    response = client.get(
        "/audit/logs",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_audit_without_token(client):
    response = client.get(
        "/audit/logs"
    )

    assert response.status_code == 401


def test_prediction_creates_audit_log(client):
    admin_token = get_admin_token(client)

    prediction_response = client.post(
        "/predictions/CUS-0001",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert prediction_response.status_code == 200

    audit_response = client.get(
        "/audit/logs",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert audit_response.status_code == 200

    logs = audit_response.json()

    assert isinstance(logs, list)

    prediction_logs = [
        log
        for log in logs
        if log["action"] == "PREDICTION_CREATED"
    ]

    assert len(prediction_logs) > 0
