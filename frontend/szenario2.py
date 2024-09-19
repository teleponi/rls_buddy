import json

import requests


BASE_URL = "http://localhost:8080"


def get_token(email, password):
    """Retrieve Token from Token Endpoint."""
    url = f"{BASE_URL}/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "password",
        "username": email,
        "password": password,
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def create_sleep_tracking(token, duration, date, quality, symptoms):
    """Create a sleep tracking entry."""
    url = f"{BASE_URL}/trackings/sleep"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "duration": duration,
        "date": date,
        "quality": quality,
        "symptoms": symptoms,
        "comment": "",
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()


def delete_user(token):
    """Delete a user."""
    url = f"{BASE_URL}/users/me/delete"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.delete(url, headers=headers)
    return response.json()


def get_sleep_tracking(token):
    """Attempt to retrieve a user's sleep tracking entries."""
    url = f"{BASE_URL}/trackings/me?type=sleep"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        print("Sleep tracking not found (expected).")
    else:
        response.raise_for_status()
        return response.json()


def create_new_user(email, password, name):
    url = f"{BASE_URL}/users"

    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password, "name": name}

    requests.post(url, json=payload, headers=headers)
    return get_token(email, password)


def main():
    email = "obob@example.com"
    password = "secret"
    token = create_new_user(email, password, "Bhob")

    # Get token
    print("Token retrieved:", token)

    # Create sleep tracking entry
    sleep_tracking = create_sleep_tracking(
        token, 8, "2024-07-01T22:00:00", "good", [1, 2]
    )
    print("Created sleep tracking:", sleep_tracking)

    # Delete user
    delete_response = delete_user(token)
    print("User deleted:", delete_response)

    # Attempt to get sleep tracking (should result in 404)
    get_sleep_tracking(token)


if __name__ == "__main__":
    main()
