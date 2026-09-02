from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user():
    unique_id = uuid4().hex[:8]

    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return email, password


def login_user(email, password):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def test_register_user():
    email, password = create_test_user()

    assert email is not None
    assert password == "TestPassword123!"


def test_login_user():
    email, password = create_test_user()

    token = login_user(email, password)

    assert token is not None
    assert isinstance(token, str)


def test_invalid_login():
    email, _ = create_test_user()

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


def test_get_notifications():
    email, password = create_test_user()
    token = login_user(email, password)

    response = client.get(
        "/notifications",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_notification():
    email, password = create_test_user()
    token = login_user(email, password)

    response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "message": "Automated test notification",
            "type": "success",
            "is_read": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Automated test notification"
    assert data["type"] == "success"
    assert data["is_read"] is False
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_create_notification_invalid_type():
    email, password = create_test_user()
    token = login_user(email, password)

    response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "message": "Invalid type test",
            "type": "random",
            "is_read": False
        }
    )

    assert response.status_code == 422


def test_mark_notification_as_read():
    email, password = create_test_user()
    token = login_user(email, password)

    create_response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "message": "Read test",
            "type": "message",
            "is_read": False
        }
    )

    assert create_response.status_code == 200

    notification_id = create_response.json()["id"]

    response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_get_single_notification():
    email, password = create_test_user()
    token = login_user(email, password)

    create_response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "message": "Single notification test",
            "type": "alert",
            "is_read": False
        }
    )

    assert create_response.status_code == 200

    notification_id = create_response.json()["id"]

    response = client.get(
        f"/notifications/{notification_id}",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["id"] == notification_id


def test_delete_notification():
    email, password = create_test_user()
    token = login_user(email, password)

    create_response = client.post(
        "/notifications",
        headers=auth_headers(token),
        json={
            "message": "Delete test",
            "type": "warning",
            "is_read": False
        }
    )

    assert create_response.status_code == 200

    notification_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/notifications/{notification_id}",
        headers=auth_headers(token)
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        f"/notifications/{notification_id}",
        headers=auth_headers(token)
    )

    assert get_response.status_code == 404


def test_user_cannot_access_another_users_notification():
    email1, password1 = create_test_user()
    token1 = login_user(email1, password1)

    email2, password2 = create_test_user()
    token2 = login_user(email2, password2)

    create_response = client.post(
        "/notifications",
        headers=auth_headers(token1),
        json={
            "message": "Private notification",
            "type": "system",
            "is_read": False
        }
    )

    assert create_response.status_code == 200

    notification_id = create_response.json()["id"]

    response = client.get(
        f"/notifications/{notification_id}",
        headers=auth_headers(token2)
    )

    assert response.status_code == 404


def test_unauthenticated_notifications():
    response = client.get("/notifications")

    assert response.status_code == 401