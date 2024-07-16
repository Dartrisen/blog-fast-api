from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from routers.auth import get_current_user
from database import SessionLocal
from models import Post

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
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreatePostRequest(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


@router.get("/", status_code=status.HTTP_200_OK)
async def get_posts(user: user_dependency, db: db_dependency, limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    query = db.query(Post).filter(Post.owner_id == user.get("id"))

    if search:
        query = query.filter(Post.title.contains(search))

    posts = query.offset(skip).limit(limit).all()
    return posts
