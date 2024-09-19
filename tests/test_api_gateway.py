import requests


API_TEST_GATEWAY_URL = "http://127.0.0.1:8080"


def test_root_check():
    response = requests.get(f"{API_TEST_GATEWAY_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Gateway"}


def test_proxy_user_docs():
    response = requests.get(f"{API_TEST_GATEWAY_URL}/user-docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text  # Assuming the docs return this
    assert "User" in response.text  # Assuming the docs return this


def test_proxy_tracking_docs():
    response = requests.get(f"{API_TEST_GATEWAY_URL}/tracking-docs")
    assert response.status_code == 200
    assert "Tracking" in response.text  # Assuming the docs return this
