"""Comments: readable by anyone, writable only by authenticated users."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_user, get_current_user_optional
from app.core.permissions import ensure_author_can_see_draft, ensure_owner_or_admin
from app.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut
from app.services.moderation_service import screen_text
from app.services.post_service import get_post_or_404
from app.utils.cache import invalidate_prefix

router = APIRouter(tags=["comments"])


@router.get("/api/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(post_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    post = get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    return db.execute(
        select(Comment).options(joinedload(Comment.author)).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    ).scalars().all()


@router.post("/api/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post = get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    screen_text(payload.content)
    comment = Comment(content=payload.content, post_id=post_id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    invalidate_prefix("posts:list:")
    return comment


@router.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    ensure_owner_or_admin(current_user, comment.author_id, action="delete this comment")
    db.delete(comment)
    db.commit()
    invalidate_prefix("posts:list:")
