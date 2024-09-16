"""
Posts router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Post
from routers.auth import get_current_user
from schemas import PostRequest, PostResponse, UpdatePostRequest

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
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


@router.get("/", response_model=list[PostResponse], status_code=status.HTTP_200_OK)
async def get_posts(user: user_dependency, db: db_dependency, limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    """Retrieve a list of posts for the current user.

    :param user: The current authenticated user.
    :param db: The database session.
    :param limit: The maximum number of posts to return (default is 10).
    :param skip: The number of posts to skip (default is 0).
    :param search: An optional search term to filter posts by title.

    :raises HTTPException: If the user is not authenticated.

    :return: A list of posts owned by the current user.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    query = db.query(Post).filter(Post.owner_id == user.get("id"))

    if search:
        query = query.filter(Post.title.contains(search))

    posts = query.offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(post_id: int, user: user_dependency, db: db_dependency):
    """Retrieve a specific post by its ID.

    :param post_id: The ID of the post to retrieve.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the post is not found.

    :return: The requested post.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    post_model = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.get("id")).first()

    if post_model is not None:
        return post_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.post("/create_post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(create_post_request: PostRequest, user: user_dependency, db: db_dependency):
    """Create a new post for the current user.

    :param create_post_request: The request object containing the new post's details.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated.

    :return: The created post.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

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
async def update_post(post_id: int, post: UpdatePostRequest, user: user_dependency, db: db_dependency):
    """Update an existing post by its ID.

    :param post_id: The ID of the post to update.
    :param post: The updated post data.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the post does not exist.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.get("id")).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    db_post.title = post.title
    db_post.content = post.content
    db_post.published = post.published

    db.commit()
    db.refresh(db_post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, user: user_dependency, db: db_dependency):
    """Delete a specific post by its ID.

    :param post_id: The ID of the post to delete.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the post does not exist.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user.get("id")).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    db.delete(db_post)
    db.commit()
