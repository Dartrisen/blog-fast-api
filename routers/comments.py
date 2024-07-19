from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Post
from routers.auth import get_current_user

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CommentCreate(BaseModel):
    content: str
    post_id: int = Field(lt=0)


class CommentUpdate(BaseModel):
    content: Optional[str]


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int

    class Config:
        orm_mode = True