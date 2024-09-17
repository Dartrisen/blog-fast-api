"""
Test admin router.
"""
from starlette import status

from routers.admin import get_db, get_current_superuser
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_create_superuser_as_superuser(test_user):
    """Test creating a superuser as an authenticated superuser."""
    app.dependency_overrides[get_current_superuser] = override_get_current_user

    request_data = {
        "username": "new_superuser",
        "email": "new_superuser@example.com",
        "password": "newpassword",
        "is_superuser": True
    }
    response = client.post("/admin", json=request_data)

    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.username == request_data["username"]
    assert model.email == request_data["email"]
    assert model.is_superuser == request_data["is_superuser"]


def test_create_superuser_as_non_superuser(test_user):
    """Test creating a superuser as an authenticated non-superuser."""
    app.dependency_overrides[get_current_superuser] = override_get_current_non_superuser

    response = client.post("/admin", json={
        "username": "new_superuser",
        "email": "new_superuser@example.com",
        "password": "newpassword",
        "is_superuser": True
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Only admins can create admin users."
