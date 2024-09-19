from unittest.mock import MagicMock, patch

from crud import get_user, get_user_by_email, get_user_by_id


def test_create_user(client, db):
    response = client.post(
        "/users/",
        json={
            "name": "Test_User",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert get_user_by_email(db, "testuser@example.com").email == "testuser@example.com"


def test_get_token(items, client):
    data = {
        "username": "waldo@parillo.com",
        "password": "123456",
    }
    response = client.post("/token", data=data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_create_user_and_get_me(db, client):
    email = "whacko@radioshack.com"
    json = {"name": "Darko", "email": email, "password": "parillada123"}
    # Create a new user
    response = client.post("/users/", json=json)
    assert response.status_code == 201
    assert response.json()["email"] == email

    # Log in to get a token
    json.pop("name")
    json["username"] = json.pop("email")
    login_response = client.post("/token", data=json)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email
    assert len(get_user(db)) == 1


def test_delete_user(items, db, client, monkeypatch):
    """Test that a user can be deleted.

    to make it work, we had to mock the publish_user_delete_event function,
    which in production sends a message to the RabbitMQ Event Queue,
    when user is deleted.
    """
    mock_publish_event = MagicMock()
    monkeypatch.setattr("routers.user.publish_user_delete_event", mock_publish_event)

    json = {
        "username": "waldo@parillo.com",
        "password": "123456",
    }
    response = client.post("/token", data=json)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/users/me", headers=headers)
    assert response.status_code == 204

    # Verify that the user was actually deleted
    assert get_user_by_id(db, 2) is None
    mock_publish_event.assert_called_once_with({"type": "USER_DELETED", "user_id": 2})
