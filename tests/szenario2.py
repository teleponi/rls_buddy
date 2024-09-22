import json

import requests
from rich.console import Console
from rich.table import Table


BASE_URL = "http://localhost:8080"

console = Console()

table = Table(show_header=True, header_style="bold magenta")
table.add_column("Action", style="dim", width=30)
table.add_column("Expected Status Code")
table.add_column("Final Status Code", justify="right")


def create_symptoms():
    url = f"{BASE_URL}/details/symptoms"
    for symptom in ["headache", "stomach ache", "nausea", "dizziness"]:
        payload = {"name": symptom}
        requests.post(url, json=payload)


def create_triggers():
    url = f"{BASE_URL}/details/triggers"
    for trigger, category in [
        ("Süßigkeiten", "food"),
        ("Kaffee", "food"),
        ("Rauchen", "lifestyle"),
        ("Ausdauersport", "lifestyle"),
        ("Stress", "emotion"),
        ("Angst", "emotion"),
        ("Laute Geräusche", "environment"),
        ("Helles Licht", "environment"),
        ("Schlafmangel", "lifestyle"),
        ("Koffeinhaltige Getränke", "food"),
    ]:
        payload = {"name": trigger, "category": category}
        requests.post(url, json=payload)


def get_token(email, password):
    """Retrieve Token from Token Endpoint."""
    url = f"{BASE_URL}/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "username": email,
        "password": password,
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def get_all_trackings(user_id):
    url = f"{BASE_URL}/trackings"
    response = requests.get(url, params={"user_id": user_id})
    return response


def create_sleep_tracking(token, duration, date, quality, symptoms, comment):
    """Create a sleep tracking entry."""
    url = f"{BASE_URL}/trackings/sleep"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "duration": duration,
        "date": date,
        "quality": quality,
        "symptoms": symptoms,
        "comment": comment,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response


def create_day_tracking(
    token, date, comment, triggers, late_morning_symptoms, afternoon_symptoms
):
    """Create a day tracking entry."""
    url = f"{BASE_URL}/trackings/day"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "date": date,
        "triggers": triggers,
        "late_morning_symptoms": late_morning_symptoms,
        "afternoon_symptoms": afternoon_symptoms,
        "comment": comment,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response


def delete_user(token):
    """Delete a user."""
    url = f"{BASE_URL}/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.delete(url, headers=headers)
    return response


def get_sleep_tracking(token):
    """Attempt to retrieve a user's sleep tracking entries."""
    url = f"{BASE_URL}/trackings/me?type=sleep"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        return response
    else:
        response.raise_for_status()
        return response


def create_new_user(email, password, name):
    url = f"{BASE_URL}/users"

    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password, "name": name}

    requests.post(url, json=payload, headers=headers)
    return get_token(email, password)


def get_random_date():
    import datetime
    import random

    year = random.randint(2010, 2024)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return str(datetime.date(year, month, day).isoformat())


def print_stars(n):
    print("*" * n)


def main():
    create_symptoms()
    create_triggers()

    print("Szenario 2: Test der Datenkonsistenz")

    username = "Odo"
    email = "odo@example.com"
    password = "secret"

    token = create_new_user(email, password, username)

    table.add_row("Create User", "201", "201")

    # Create sleep tracking entry
    sleep_tracking = create_sleep_tracking(
        token, 8, get_random_date(), "good", [1, 2], "I slept well."
    )
    assert sleep_tracking.status_code == 201
    table.add_row("Create Sleep Tracking", "201", "201")

    # Create day tracking entry
    day_tracking = create_day_tracking(
        token, get_random_date(), "I felt good today.", [1, 2], [1, 2], [1, 2]
    )
    assert day_tracking.status_code == 201
    table.add_row("Create Day Tracking", "201", "201")

    # Get sleep tracking
    result = get_sleep_tracking(token)
    assert result.status_code == 200
    table.add_row("Get Sleep Tracking", "200", "200")

    # Delete user
    delete_response = delete_user(token)
    assert delete_response.status_code == 204
    table.add_row("Delete User", "204", "204")

    # Attempt to get get old users sleep trackings (should result in 401)
    result = get_sleep_tracking(token)
    assert result.status_code == 401
    table.add_row("Get Sleep Tracking (Unauthorized)", "401", "401")

    # attempt to get all trackings of this user (internal endpoint)
    result = get_all_trackings(1)
    assert result.status_code == 404
    table.add_row("Get All Trackings", "404", "404")

    console.print(table)


if __name__ == "__main__":
    main()
