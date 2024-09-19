"""
Simple Tool to demonstrate the work of the API

SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'trackings';

FOOD = "food"
ENVIRONMENT = "environment"
LIFESTYLE = "lifestyle"
EMOTION = "emotion"
OTHER = "other"

"""

import pydantic
import requests


iu = input("enter dev (8000) or test (8001): ")
if iu == "dev":
    LOCAL_URL = "http://localhost:8000"
elif iu == "test":
    LOCAL_URL = "http://localhost:8080"
elif iu == "prod":
    LOCAL_URL = "https://rlsbuddy.spielprinzip.com"


menu = (
    "1 for create tracking",
    "2 for show trackings",
    "3 update tracking",
    "4 delete user",
    "5 for exit",
    "6 for bulk create sleep data",
    "7 create new user",
    "8 validate token",
    "9 delete tracking",
    "10 authenticate",
    "11 delete all trackings",
)


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def create_new_user():
    email = input("please enter email: ") or "bob@email.com"
    name = input("please enter name: ") or "bob"
    password = input("please enter password: ") or "secret"
    create_user(email, password, name)
    return get_token(email, password)


def bulk_create_trackings(type):
    bulk_data = auto_create_data(type)
    for data in bulk_data:
        response = create_tracking(token, (data, type), update=False)
        print(response)


def init_data(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{LOCAL_URL}/details/triggers"
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
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())

    url = f"{LOCAL_URL}/details/symptoms"
    for symptom in ["headache", "stomach ache", "nausea", "dizziness"]:
        payload = {"name": symptom}
        response = requests.post(url, json=payload, headers=headers)
        print(response.json())


def validate_token(token):
    url = f"{LOCAL_URL}/trackings/health"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print("R:", response.json())


def enter_triggers():
    url = f"{LOCAL_URL}/details/triggers"
    response = requests.get(url)
    triggers = []
    list_of_triggers = response.json()
    while True:
        print("list of triggers:", list_of_triggers)
        trigger = input("please enter trigger: ")
        triggers.append(int(trigger))
        more = input("do you want to enter more triggers? (y/n): ")
        if more == "n":
            break
    return triggers


def enter_symptoms():
    url = f"{LOCAL_URL}/details/symptoms"
    response = requests.get(url)
    symptoms = []
    list_of_symptoms = response.json()
    while True:
        print("list of symptoms:", list_of_symptoms)
        symptom = input("please enter symptom: ")
        symptoms.append(int(symptom))
        more = input("do you want to enter more symptoms? (y/n): ")
        if more == "n":
            break
    return symptoms


def get_tracking_data(update: bool = False) -> tuple[dict, str]:
    tracking_type = input("please enter type of tracking: (sleep, mood, symptom): ")

    if tracking_type == "sleep" or tracking_type == "mood":
        duration = input("please enter duration: ")
        quality = input("please enter sleep quality (bad, moderate, good): ")
        add_symptoms = input("do you want to add symptoms? (y/n): ")

        symptoms = []
        if add_symptoms == "y":
            symptoms = enter_symptoms()
        payload = {
            "duration": duration,
            "quality": quality,
            "symptoms": symptoms,
            "comment": "",
        }
        if not update:
            payload["date"] = input("please enter date: YYYY-MM-DD: ")
    elif tracking_type == "day":
        add_triggers = input("do you want to add triggers? (y/n): ")

        triggers = []
        if add_triggers == "y":
            triggers = enter_triggers()

        payload = {
            "comment": "",
            "triggers": triggers,
            "late_morning_symptoms": [1, 2],
            "afternoon_symptoms": [1, 2],
        }
        print("payload", payload)
        if not update:
            payload["date"] = input("please enter date: YYYY-MM-DD: ")

    return payload, tracking_type


def auto_create_data(type: str) -> list[dict] | None:
    trackings = {
        "sleep": [
            {
                "duration": 8,
                "quality": "good",
                "symptoms": [1, 2],
                "date": "2021-10-01",
                "comment": "good sleep",
            },
            {
                "duration": 7,
                "quality": "good",
                "symptoms": [1],
                "date": "2021-10-07",
                "comment": "good sleep",
            },
        ],
        "day": [
            {
                "date": "2021-10-01",
                "comment": "godd day",
                "triggers": [1, 3],
                "late_morning_symptoms": [1, 2],
                "afternoon_symptoms": [1, 2],
            },
            {
                "comment": "godd day",
                "date": "2021-10-04",
                "triggers": [1, 2],
                "late_morning_symptoms": [1],
                "afternoon_symptoms": [2],
            },
            {
                "comment": "godd day",
                "date": "2021-10-05",
                "triggers": [1, 2, 3],
                "late_morning_symptoms": [],
                "afternoon_symptoms": [],
            },
            {
                "comment": "godd day",
                "date": "2021-10-06",
                "late_morning_symptoms": [],
                "afternoon_symptoms": [],
                "triggers": [2],
            },
        ],
    }
    data = trackings.get(type)
    return data


def create_tracking(token, data, update=False):
    payload, tracking_type = data
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if update:
        ui = input("please enter tracking id: ")
        url = f"{LOCAL_URL}/trackings/{tracking_type}/{ui}"
        response = requests.put(url, json=payload, headers=headers)
    else:
        url = f"{LOCAL_URL}/trackings/{tracking_type}"
        response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json(), 200  # Returns the response as a dictionary
    else:
        return response.text, response.status_code


def get_my_trackings(token):
    url = f"{LOCAL_URL}/trackings/me"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start_date = None
    end_date = None

    tracking_type = input("which type of tracking do you want to see? (sleep, day): ")
    params = {
        "type": tracking_type,
    }
    choose_dates = input("do you want to enter dates? (y/n): ")
    if choose_dates == "y":
        start_date = input("please enter start date (YYYY-MM-DD): ")
        end_date = input("please enter end date (YYYY-MM-DD): ")

    if start_date and end_date:
        params |= {
            "start_date": start_date,
            "end_date": end_date,
        }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()  # Returns the response as a dictionary
    else:
        print(response.status_code)
        print(response.json())


def create_user(email, password, name):
    """Create a new user."""
    print("creating user ....")
    url = f"{LOCAL_URL}/users"
    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password, "name": name}

    response = requests.post(url, json=payload, headers=headers)
    print("USER RESPONSE:", response.status_code)

    if response.status_code == 201:
        print("user created")
    else:
        print("user could not be created")
        print(response.status_code)
        print(response.json())
        # exit()


def get_token(email: str, password: str) -> str | None:
    """Retrieve Token from Token Endpoint."""

    print("retrieving token...")
    url = f"{LOCAL_URL}/token"
    # headers = {"Content-Type": "application/json"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"username": email, "password": password}

    response = requests.post(url, data=payload, headers=headers)
    print("TOKEN:", response.json())

    if response.status_code == 200:
        token = Token(**response.json())
        print("token retrieved", response.json())
        return token.access_token
    else:
        print(response.status_code)
        print("could not retrieve token")

    return None


def delete_user(token):
    url = f"{LOCAL_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print("user deleted")
    else:
        print(response.status_code)


def delete_tracking(token, tracking_id):
    url = f"{LOCAL_URL}/trackings/sleep/{tracking_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("tracking deleted")
    else:
        print("tracking NOT deleted")
        print(response.status_code)
        print(response.json())


def delete_all_trackings(token):
    url = f"{LOCAL_URL}/trackings/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("trackings deleted")
    else:
        print("tracking NOT deleted")
        print(response.status_code)
        print(response.json())


def read_user(token):
    url = f"{LOCAL_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("user:", response.json())
    else:
        print(response.status_code)


def create_tracking_ui(token):
    """Create Tracking User input."""
    symptom = input("please enter symtom: ")
    severity = input("please enter severity: ")
    print("creating tracking...")

    try:
        tracking = create_tracking(token, symptom, severity)
        print("tracking created")
        print(tracking)
    except requests.HTTPError as e:
        print(e)
        print("could not create tracking")


def try_retry(email, password, name):
    token = get_token(email, password)
    if not token:
        create_user(email, password, name)
        token = get_token(email, password)
    return token


if __name__ == "__main__":
    email = "alice@example2.com"
    name = "hase"
    password = "1234"
    token = try_retry(email, password, name)
    init_data(token)
    read_user(token)

    while True:
        [print(menu_point) for menu_point in menu]
        choice = input("please enter choice: ")
        if choice == "1":
            data = get_tracking_data()
            response = create_tracking(token, data, update=False)
            print(response)
        elif choice == "2":
            if response := get_my_trackings(token):
                if "error" not in response:
                    for row in response:
                        print(row)
                else:
                    print(response["error"])
        elif choice == "3":
            print("update tracking")
            data = get_tracking_data(update=True)
            response = create_tracking(token, data, update=True)
            print(response)
        elif choice == "5":
            exit(0)
        elif choice == "4":
            delete = input("are you sure you want to delete user? (y/n): ")
            if delete == "y":
                delete_user(token)
        elif choice == "6":
            bulk_create = input("which tracking to bulk create? (sleep/day): ")
            bulk_create_trackings(bulk_create)
        elif choice == "7":
            token = create_new_user()
        elif choice == "8":
            validate_token(token)
        elif choice == "9":
            tracking_id = input("which sleep tracking to delete? ")
            delete_tracking(token, tracking_id)
        elif choice == "11":
            tracking_delete = input("really want to delete all trackings? (y/n): ")
            if tracking_delete == "y":
                delete_all_trackings(token)

        else:
            print("invalid choice")
            continue
