"""
Comments router.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Post, Comment
from routers.auth import get_current_user
from routers.posts import get_post
from schemas import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
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
post_dependency = Annotated[dict, Depends(get_post)]


@router.get("/", response_model=list[CommentResponse], status_code=status.HTTP_200_OK)
async def get_comments(post_id: int, user: user_dependency, db: db_dependency, limit: int = 10, skip: int = 0):
    """Retrieve comments for a specific post.

    :param post_id: The ID of the post.
    :param user: The current authenticated user.
    :param db: The database session.
    :param limit: The maximum number of comments to return (default is 10).
    :param skip: The number of comments to skip (default is 0).

    :raises HTTPException: If the user is not authenticated or the post is not found.

    :return: A list of comments related to the post.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comments = db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
    return comments


@router.get("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def get_comment(comment_id: int, user: user_dependency, db: db_dependency):
    """Retrieve a specific comment by its ID.

    :param comment_id: The ID of the comment.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the comment is not found.

    :return: The requested comment.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    return db_comment


@router.post("/create_comment", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate, post: post_dependency, user: user_dependency, db: db_dependency):
    """Create a new comment on a post.

    :param comment: The comment data to create.
    :param post: The associated post data.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated.

    :return: The created comment.
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_comment = Comment(
        content=comment.content,
        post_id=post.id,
        author_id=user.get("id")
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment


@router.put("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(comment_id: int, comment: CommentUpdate, user: user_dependency, db: db_dependency):
    """Update an existing comment by its ID.

    :param comment_id: The ID of the comment to update.
    :param comment: The updated comment data.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the comment does not exist.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == user.get("id")).first()
    if db_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    db_comment.content = comment.content

    db.commit()
    db.refresh(db_comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, user: user_dependency, db: db_dependency):
    """Delete a specific comment by its ID.

    :param comment_id: The ID of the comment to delete.
    :param user: The current authenticated user.
    :param db: The database session.

    :raises HTTPException: If the user is not authenticated or the comment does not exist.

    :return: None
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == user.get("id")).first()
    if db_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    db.delete(db_comment)
    db.commit()
