import pytest
from httpx import AsyncClient
from main import app


# Mock service URLs for testing purposes
USER_SERVICE_URL = "http://user-service-url.com"
TRACKING_SERVICE_URL = "http://tracking-service-url.com"

client = AsyncClient(app=app, base_url="http://test")


class MockResponse:
    def __init__(self, content, status_code):
        self.content = content.encode()  # Content must be bytes
        self.status_code = status_code
        self.headers = {"content-type": "text/html"}

    @property
    def text(self):
        return self.content.decode()

    def json(self):
        return {"message": self.content.decode()}


@pytest.mark.asyncio
async def test_proxy_user_docs(monkeypatch):
    async def mock_get(*args, **kwargs):
        return MockResponse(content="User Docs", status_code=200)

    # Monkeypatch the httpx.AsyncClient.get method
    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/user-docs")

    assert response.status_code == 200
    assert response.text == "User Docs"


# Test tracking-docs proxy using monkeypatch
@pytest.mark.asyncio
async def test_proxy_tracking_docs(monkeypatch):
    async def mock_get(*args, **kwargs):
        return MockResponse(content="Tracking Docs", status_code=200)

    # Monkeypatch the httpx.AsyncClient.get method
    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/tracking-docs")

    assert response.status_code == 200
    assert response.text == "Tracking Docs"


@pytest.mark.asyncio
async def test_user_service_proxy(monkeypatch):
    async def mock_request(*args, **kwargs):
        return MockResponse(content="User Service Response", status_code=200)

    monkeypatch.setattr("httpx.AsyncClient.request", mock_request)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/profile")

    assert response.status_code == 200
    assert response.text == "User Service Response"


# Test service not found (404) case
@pytest.mark.asyncio
async def test_service_not_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/unknown-service/path")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service not found"}


@pytest.mark.asyncio
async def test_read_root():
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Gateway"}


# The function to test
def determine_service_url(path: str) -> str:
    if path.startswith("users") or path.startswith("token"):
        return USER_SERVICE_URL
    elif path.startswith("trackings") or path.startswith("details"):
        return TRACKING_SERVICE_URL
    return None


# Pytest unit tests
def test_user_service_url_with_users():
    assert determine_service_url("users/profile") == USER_SERVICE_URL


def test_user_service_url_with_token():
    assert determine_service_url("token/generate") == USER_SERVICE_URL


def test_tracking_service_url_with_trackings():
    assert determine_service_url("trackings/12345") == TRACKING_SERVICE_URL


def test_tracking_service_url_with_details():
    assert determine_service_url("details/shipment") == TRACKING_SERVICE_URL


def test_none_return_for_unrecognized_path():
    assert determine_service_url("orders/123") is None


def test_empty_string():
    assert determine_service_url("") is None


def test_partial_matching():
    assert determine_service_url("userdetails") is None  # Should not match
