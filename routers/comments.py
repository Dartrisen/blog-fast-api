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
    content: str = Field(min_length=1, max_length=300)
    # post_id: int = Field(gt=0)


class CommentUpdate(BaseModel):
    content: Optional[str]


class CommentResponse(BaseModel):
    id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=300)
    post_id: int = Field(gt=0)
    author_id: int = Field(gt=0)

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


@router.get("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def get_comment(comment_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    return db_comment


@router.post("/create_comment", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate, post: post_dependency, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_comment = Comment(
        content=comment.content,
        post_id=post.id,
        author_id=user.get("id")
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment
