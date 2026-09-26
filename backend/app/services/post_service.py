"""Business logic for posts: create/update/delete with ownership + slug
generation + cache invalidation."""
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus
from app.models.post_view import PostView
from app.models.user import User
from app.repositories import post_repository
from app.schemas.post import PostCreate, PostUpdate
from app.services.moderation_service import screen_text
from app.utils.cache import invalidate_prefix
from app.utils.slugify import slugify


def create_post(db: Session, author: User, payload: PostCreate, cover_image_url: str | None) -> Post:
    screen_text(f"{payload.title}\n{payload.content}")
    post = Post(
        title=payload.title,
        slug=slugify(payload.title),
        content=payload.content,
        excerpt=payload.excerpt,
        tags=payload.tags,
        status=payload.status,
        cover_image_url=cover_image_url,
        author_id=author.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    invalidate_prefix("posts:list:")
    return post


def record_view(db: Session, post: Post, current_user: User | None, reader_id: str | None) -> None:
    """Count one view per person. The author, a draft, and a repeat open do not count."""
    if post.status != PostStatus.PUBLISHED:
        return
    if current_user and current_user.id == post.author_id:
        return
    if current_user:
        viewer_key = f"user:{current_user.id}"
    elif reader_id:
        viewer_key = f"reader:{reader_id.strip()[:64]}"
    else:
        return
    db.add(PostView(post_id=post.id, viewer_key=viewer_key))
    post.view_count = (post.view_count or 0) + 1
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def get_post_or_404(db: Session, post_id: int) -> Post:
    post = post_repository.get_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def update_post(db: Session, post: Post, payload: PostUpdate) -> Post:
    data = payload.model_dump(exclude_unset=True)
    if "title" in data or "content" in data:
        screen_text(f"{data.get('title', post.title)}\n{data.get('content', post.content)}")
    for field, value in data.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    invalidate_prefix("posts:list:")
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()
    invalidate_prefix("posts:list:")
