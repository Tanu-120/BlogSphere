"""Load sample accounts and posts when the database does not already have them."""
import logging
import shutil
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.sample_content import (
    ADMIN_EMAIL,
    AUTHOR_EMAIL,
    DEMO_PASSWORD,
    DRAFT,
    POSTS,
    READER_EMAIL,
)

logger = logging.getLogger(__name__)
_COVERS = Path(__file__).resolve().parent / "sample_covers"


def _install_cover(filename: str | None) -> str | None:
    if not filename:
        return None
    source = _COVERS / filename
    if not source.is_file():
        return None
    dest_dir = Path(get_settings().UPLOAD_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest_dir / filename)
    return f"/uploads/{filename}"


def _user(db: Session, *, name: str, email: str, role: UserRole, bio: str) -> User:
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        return existing
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        bio=bio,
    )
    db.add(user)
    db.flush()
    return user


def _upsert_post(db: Session, author_id: int, spec: dict) -> Post:
    post = db.scalar(select(Post).where(Post.slug == spec["slug"]))
    is_new = post is None
    if is_new:
        post = Post(slug=spec["slug"], author_id=author_id, title=spec["title"], content=spec["content"])
        post.view_count = spec["view_count"]
        db.add(post)
    post.title = spec["title"]
    post.content = spec["content"]
    post.excerpt = spec["excerpt"]
    post.tags = spec["tags"]
    post.cover_image_url = _install_cover(spec.get("cover"))
    post.status = PostStatus(spec["status"])
    post.ai_summary = spec["ai_summary"]
    post.ai_tags = spec["ai_tags"]
    post.created_at = spec["created_at"]
    post.updated_at = spec["created_at"]
    post.author_id = author_id
    db.flush()
    return post


def seed_demo_data() -> None:
    """Refresh sample accounts, essays, and cover photos. Existing view counts, likes, and comments are left as they are."""
    if not get_settings().SEED_DEMO_DATA:
        return

    db = SessionLocal()
    try:
        author = _user(
            db,
            name="Tanu Sharma",
            email=AUTHOR_EMAIL,
            role=UserRole.USER,
            bio="Writes about publishing, models, and the boring parts that keep a site honest.",
        )
        _user(
            db,
            name="ABC",
            email=READER_EMAIL,
            role=UserRole.USER,
            bio="A second member account, with no posts of its own.",
        )
        _user(
            db,
            name="Tanu Sharma",
            email=ADMIN_EMAIL,
            role=UserRole.ADMIN,
            bio="Moderates the journal. Can remove a post or comment and review the audit log.",
        )

        for spec in POSTS:
            _upsert_post(db, author.id, spec)
        _upsert_post(db, author.id, DRAFT)

        db.commit()
        logger.info("Sample posts refreshed (%s published)", len(POSTS))
    except Exception:
        db.rollback()
        logger.exception("Sample data was not loaded; the API will still start")
    finally:
        db.close()
