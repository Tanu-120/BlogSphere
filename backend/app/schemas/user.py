from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    bio: str | None = None
    avatar_url: str | None = None
    role: UserRole
    created_at: datetime


class UserMe(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe
