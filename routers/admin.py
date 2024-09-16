"""
Admins router.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from .auth import get_current_user, get_password_hash
from schemas import CreateSuperUserRequest

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


def get_db():
    """Dependency that provides a database session.

    :return: A generator that yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def get_current_superuser(user: user_dependency):
    """Ensure the current user is a superuser.

    :param user: The current authenticated user.

    :raises HTTPException: If the user does not have superuser privileges.

    :return: The current user if they are a superuser.
    """
    if not user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_superuser(
        create_superuser_request: CreateSuperUserRequest,
        db: db_dependency,
        current_user: User = Depends(get_current_superuser)
):
    """Create a new superuser.

    :param create_superuser_request: The request object containing the new superuser's details.
    :param db: The database session.
    :param current_user: The current authenticated superuser.

    :raises HTTPException: If the current user is not a superuser or if an attempt is made to create an admin user by a non-admin.

    :return: None
    """
    if create_superuser_request.is_superuser == True and not current_user.get("is_superuser"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create admin users.")

    create_user_model = User(
        username=create_superuser_request.username,
        email=create_superuser_request.email,
        is_superuser=create_superuser_request.is_superuser,
        hashed_password=get_password_hash(create_superuser_request.password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
