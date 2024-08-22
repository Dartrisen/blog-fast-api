from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class CreateSuperUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = Field(True)


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = Field(default=False)


class Token(BaseModel):
    access_token: str
    token_type: str


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=300)


class CommentUpdate(BaseModel):
    content: Optional[str]


class CommentResponse(BaseModel):
    id: int = Field(gt=0)
    content: str = Field(min_length=1, max_length=300)
    post_id: int = Field(gt=0)
    author_id: int = Field(gt=0)

    class Config:
        from_attributes = True


class PostRequest(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=5000)
    published: Optional[bool] = True


class PostResponse(PostRequest):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UpdatePostRequest(PostRequest):
    ...
