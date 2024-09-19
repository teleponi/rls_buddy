import pytest
from pydantic import ValidationError
from schemes import UserCreate


@pytest.mark.parametrize("name", [["a"], ["abas?"], ["-bbb"]])
def test_create_user_with_short_name(name):
    """Test to ensure short names raise ValidationError."""
    with pytest.raises(ValidationError):
        UserCreate(name=name, email="testuser@example.com", password="password123")


def test_create_user_with_invalid_email():
    """Test to ensure invalid email raises ValidationError."""
    with pytest.raises(ValidationError):
        UserCreate(name="Abc", email="testuser.com", password="password123")


def test_create_user_with_valid_name():
    """Test user creation with valid name and email."""
    user = UserCreate(
        name="Test_User", email="testuser@example.com", password="password123"
    )
    assert user.name == "Test_User"
    assert user.email == "testuser@example.com"
