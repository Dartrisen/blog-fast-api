from datetime import datetime, timedelta, timezone
from typing import Annotated, Type

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "557194d75e3f6ac06f08816bc59f0f62e1093542bb9104d229baeda94e7c6ba7"
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str
