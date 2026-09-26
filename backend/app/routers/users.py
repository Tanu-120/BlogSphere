"""Profile, the signed-in user's posts, and a CSV export of those posts."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories import post_repository, user_repository
from app.schemas.post import PostListItem
from app.schemas.user import UserPublic, UserUpdate, UserMe
from app.services.serializers import posts_to_list_items
from app.utils.export import posts_to_csv

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/users/{user_id}", response_model=UserPublic)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/me", response_model=UserMe)
def update_my_profile(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users/me/posts", response_model=list[PostListItem])
def my_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns ALL of the current user's posts (drafts + published) -
    this is the 'manage my blogs' dashboard endpoint."""
    posts = post_repository.list_by_author(db, current_user.id)
    return posts_to_list_items(db, posts)


@router.get("/users/me/posts/export")
def export_my_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    posts = post_repository.list_by_author(db, current_user.id)
    csv_data = posts_to_csv(posts)
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=my_posts.csv"},
    )
