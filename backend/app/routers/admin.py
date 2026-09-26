"""
Admin-only moderation: delete any post or comment, and read the audit log.
Every mutating action here writes an AuditLog row.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.user import User
from app.core.permissions import ensure_author_can_see_draft
from app.services.post_service import get_post_or_404, delete_post
from app.utils.cache import invalidate_prefix

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _log(db: Session, admin: User, action: str, resource_type: str, resource_id: int, details: str = ""):
    db.add(AuditLog(user_id=admin.id, action=action, resource_type=resource_type, resource_id=resource_id, details=details))
    db.commit()


@router.delete("/posts/{post_id}", status_code=204)
def admin_delete_post(post_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    post = get_post_or_404(db, post_id)
    ensure_author_can_see_draft(admin, post)
    _log(db, admin, "post.delete", "post", post_id, details=f"title={post.title!r}")
    delete_post(db, post)


@router.delete("/comments/{comment_id}", status_code=204)
def admin_delete_comment(comment_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    _log(db, admin, "comment.delete", "comment", comment_id)
    db.delete(comment)
    db.commit()
    invalidate_prefix("posts:list:")


@router.get("/audit-logs")
def list_audit_logs(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    logs = db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).scalars().all()
    return [
        {
            "id": l.id, "user_id": l.user_id, "action": l.action, "resource_type": l.resource_type,
            "resource_id": l.resource_id, "details": l.details, "created_at": l.created_at,
        }
        for l in logs
    ]
