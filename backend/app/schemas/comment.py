from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    post_id: int
    author: UserPublic
    created_at: datetime
