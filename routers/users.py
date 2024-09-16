"""
Users router.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from routers.auth import get_current_user
from database import SessionLocal
from models import User

router = APIRouter(
    prefix="/user",
    tags=["user"]
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
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    """Model for user password verification.

    :param password: The current password of the user.
    :param new_password: The new password for the user (minimum length of 6 characters).
    """
    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    """Retrieve the current user's information.

    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated.

    :return: The user's information from the database.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(User).filter(User.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    """Change the current user's password.

    :param user: The current authenticated user.
    :param db: The database session.
    :param user_verification: The request object containing the current and new passwords.

    :raises HTTPException: If the user is not authenticated or the current password is incorrect.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/email/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def change_email(user: user_dependency, db: db_dependency, email: str):
    """Change the current user's email address.

    :param user: The current authenticated user.
    :param db: The database session.
    :param email: The new email address to set for the user.

    :raises HTTPException: If the user is not authenticated.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    user_model.email = email
    db.add(user_model)
    db.commit()
