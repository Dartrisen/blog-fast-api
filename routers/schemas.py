from pydantic import BaseModel, EmailStr, Field


class CreateSuperUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_superuser: bool = Field(True)
