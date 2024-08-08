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
