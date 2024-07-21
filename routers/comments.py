from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Post, Comment
from routers.auth import get_current_user
from routers.posts import get_post

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
post_dependency = Annotated[dict, Depends(get_post)]


class CommentCreate(BaseModel):
    content: str
    # post_id: int = Field(gt=0)


class CommentUpdate(BaseModel):
    content: Optional[str]


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CommentResponse], status_code=status.HTTP_200_OK)
async def get_comments(post_id: int, user: user_dependency, db: db_dependency, limit: int = 10, skip: int = 0):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
    return comments
