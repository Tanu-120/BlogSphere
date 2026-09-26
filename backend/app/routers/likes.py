"""Likes: toggle endpoint, authenticated users only."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.permissions import ensure_author_can_see_draft
from app.database import get_db
from app.models.like import Like
from app.models.user import User
from app.repositories.post_repository import like_count
from app.schemas.common import LikeStatus
from app.services.post_service import get_post_or_404
from app.utils.cache import invalidate_prefix

router = APIRouter(prefix="/api/posts", tags=["likes"])


@router.post("/{post_id}/like", response_model=LikeStatus)
def toggle_like(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    existing = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.id).first()

    if existing:
        db.delete(existing)
        db.commit()
        liked = False
    else:
        db.add(Like(post_id=post_id, user_id=current_user.id))
        db.commit()
        liked = True

    invalidate_prefix("posts:list:")
    return LikeStatus(liked=liked, like_count=like_count(db, post_id))
