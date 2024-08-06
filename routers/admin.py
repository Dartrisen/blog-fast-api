from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user, get_password_hash
from database import SessionLocal

from pydantic import BaseModel, EmailStr, Field
from models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


class CreateSuperUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = Field(True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def get_current_superuser(user: user_dependency):
    if not user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_superuser(
        create_superuser_request: CreateSuperUserRequest,
        db: db_dependency,
        current_user: User = Depends(get_current_superuser)
):
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
