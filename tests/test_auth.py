from datetime import timedelta

from fastapi import HTTPException
from jose import jwt
from starlette import status

from routers.auth import get_db, get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    """Test the user authentication function."""
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user("wrongusername", "testpassword", db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user is False


def test_create_access_token():
    """Test the creation of a JWT access token."""
    username = "testuser"
    user_id = 1
    is_superuser = False
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, is_superuser, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["is_superuser"] == is_superuser


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test retrieving the current user with a valid token."""
    encode = {"sub": "testuser", "id": 1, "is_superuser": True}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)
    assert user == {"username": "testuser", "id": 1, "is_superuser": True}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    """Test retrieving the current user with a token missing required payload."""
    encode = {"is_superuser": False}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as ex:
        await get_current_user(token=token)

    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == "Could not validate user"
