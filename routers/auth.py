"""
Authentication router.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Type

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from schemas import CreateUserRequest, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "557194d75e3f6ac06f08816bc59f0f62e1093542bb9104d229baeda94e7c6ba7"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    """Dependency that provides a database session.

    :return: A generator that yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency: Type[Session] = Annotated[Session, Depends(get_db)]


def get_password_hash(password: str) -> bytes:
    """Generate a hashed password from a plain text password.

    :param password: The plain text password to hash.

    :return: The hashed password as bytes.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to check against.

    :return: True if the passwords match, otherwise False.
    """
    pwd_bytes = plain_password.encode("utf-8")
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=pwd_bytes, hashed_password=hashed_password)


def authenticate_user(username: str, password: str, db):
    """Authenticate a user by username and password.

    :param username: The username of the user.
    :param password: The user's password.
    :param db: The database session.

    :return: The authenticated user object if successful; otherwise False.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, is_superuser: bool, expires_delta: timedelta):
    """Create an access token for a user.

    :param username: The username of the user.
    :param user_id: The ID of the user.
    :param is_superuser: Boolean indicating if the user is a superuser.
    :param expires_delta: The duration until the token expires.

    :return: A JWT access token as a string.
    """
    encode = {"sub": username, "id": user_id, "is_superuser": is_superuser}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """Get the current authenticated user from the provided token.

    :param token: The JWT access token.

    :raises HTTPException: If the token is invalid or expired.

    :return: A dictionary containing the current user's information.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        is_superuser: str = payload.get("is_superuser")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"username": username, "id": user_id, "is_superuser": is_superuser}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Create a new user in the system.

    :param db: The database session.
    :param create_user_request: The request object containing new user's details.

    :raises HTTPException: If the username or email is already registered.

    :return: None
    """
    user_model = db.query(User).filter(User.username == create_user_request.username).first()
    if user_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    user_model = db.query(User).filter(User.email == create_user_request.email).first()
    if user_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    create_user_model = User(
        username=create_user_request.username,
        email=create_user_request.email,
        is_superuser=False,
        hashed_password=get_password_hash(create_user_request.password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    """Login and obtain an access token for a user.

    :param form_data: Form data containing username and password.
    :param db: The database session.

    :raises HTTPException: If authentication fails.

    :return: A dictionary containing the access token and its type.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.id, user.is_superuser, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
