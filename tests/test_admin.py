from starlette import status

from routers.admin import get_db, get_current_superuser
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_superuser] = override_get_current_user


def test_create_superuser_as_superuser(test_user):
    request_data = {
        "username": "new_superuser",
        "email": "new_superuser@example.com",
        "password": "newpassword",
        "is_superuser": True
    }
    response = client.post("/admin", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(User).filter(User.id == 2).first()
    assert model.username == request_data["username"]
    assert model.email == request_data["email"]
    assert model.is_superuser == request_data["is_superuser"]
