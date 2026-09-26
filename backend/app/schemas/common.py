from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class LikeStatus(BaseModel):
    liked: bool
    like_count: int
