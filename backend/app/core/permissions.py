"""
Ownership and role checks.

Rule of the platform: a resource can be modified/deleted by
  1) its owner, OR
  2) a user with the ADMIN role (moderation).
Everyone else gets 403.
"""
from fastapi import HTTPException, status

from app.models.post import Post, PostStatus
from app.models.user import User, UserRole


def ensure_author_can_see_draft(current_user: User | None, post: Post) -> None:
    """A draft is visible only to the person who wrote it. Admins and other members get the same not-found as a guest."""
    if post.status == PostStatus.DRAFT and (current_user is None or current_user.id != post.author_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


def ensure_owner_or_admin(current_user: User, owner_id: int, action: str = "modify this resource") -> None:
    if current_user.id != owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to {action}",
        )
