from starlette import status

from routers.users import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    """Test retrieving the current user's information."""
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    result.pop("hashed_password")
    result.pop("created_at")
    assert result == {
        'email': 'test@test.com',
        'id': 1,
        'is_active': True,
        'is_superuser': True,
        'username': 'dartrisen',
    }


def test_change_password_success(test_user):
    """Test successfully changing the user's password."""
    response = client.put("/user/password", json={
        "password": "testpassword",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    """Test changing the user's password with an invalid current password."""
    response = client.put("/user/password", json={
        "password": "wrongpassword",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change"}


def test_change_email_success(test_user):
    """Test successfully changing the user's email address."""
    response = client.put("/user/email/test@test.com")
    assert response.status_code == status.HTTP_204_NO_CONTENT
