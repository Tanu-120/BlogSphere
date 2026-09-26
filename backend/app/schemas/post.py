from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.models.post import PostStatus
from app.schemas.user import UserPublic


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=1)
    excerpt: str | None = Field(default=None, max_length=300)
    tags: str | None = Field(default=None, description="Comma-separated tags")
    status: PostStatus = PostStatus.DRAFT


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    content: str | None = None
    excerpt: str | None = Field(default=None, max_length=300)
    tags: str | None = None
    status: PostStatus | None = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    content: str
    excerpt: str | None
    cover_image_url: str | None
    tags: str | None
    status: PostStatus
    ai_summary: str | None
    ai_tags: str | None
    view_count: int
    author: UserPublic
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    comment_count: int = 0
    liked_by_me: bool = False


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    excerpt: str | None
    cover_image_url: str | None
    tags: str | None
    status: PostStatus
    author: UserPublic
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0


class PaginatedPosts(BaseModel):
    items: list[PostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    search_models: list[str] = []
    llm: str | None = None


class AIGenerateResponse(BaseModel):
    ai_summary: str
    ai_tags: str
    source: str  # "anthropic" | "openai" | "fallback"
