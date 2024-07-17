from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Post
from routers.auth import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CreatePostRequest(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    owner_id: int

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_posts(user: user_dependency, db: db_dependency, limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    query = db.query(Post).filter(Post.owner_id == user.get("id"))

    if search:
        query = query.filter(Post.title.contains(search))

    posts = query.offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(post_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.get("id")).first()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return db_post


@router.post("/post/", status_code=status.HTTP_201_CREATED)
async def create_post(create_post_request: CreatePostRequest, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_post = Post(
        title=create_post_request.title,
        content=create_post_request.content,
        published=create_post_request.published,
        owner_id=user.get("id")
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.put("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(post_id: int, post: PostUpdate, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.get("id")).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.title is not None:
        db_post.title = post.title
    if post.content is not None:
        db_post.content = post.content
    if post.published is not None:
        db_post.published = post.published

    db.commit()
    db.refresh(db_post)
