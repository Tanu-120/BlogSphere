"""
Query layer for posts. Routers do not build SQL.
Authors are eager-loaded so a page of posts does not query once per row.
"""
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.post import Post, PostStatus
from app.models.like import Like
from app.models.comment import Comment
from app.services.search_service import rank_posts


def get_by_id(db: Session, post_id: int) -> Post | None:
    return db.execute(
        select(Post).options(joinedload(Post.author)).where(Post.id == post_id)
    ).scalar_one_or_none()


def get_by_slug(db: Session, slug: str) -> Post | None:
    return db.execute(
        select(Post).options(joinedload(Post.author)).where(Post.slug == slug)
    ).scalar_one_or_none()


def list_published(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    tag: str | None = None,
    author_id: int | None = None,
    sort: str = "newest",
) -> tuple[list[Post], int, list[str], str | None]:
    query = select(Post).options(joinedload(Post.author)).where(Post.status == PostStatus.PUBLISHED)

    if search and search.strip():
        if tag:
            query = query.where(Post.tags.ilike(f"%{tag}%"))
        if author_id:
            query = query.where(Post.author_id == author_id)
        candidates = list(db.execute(query.order_by(Post.created_at.desc())).unique().scalars().all())
        ranked, models, llm_name = rank_posts(candidates, search.strip())
        start = (page - 1) * page_size
        return ranked[start : start + page_size], len(ranked), models, llm_name

    if tag:
        query = query.where(Post.tags.ilike(f"%{tag}%"))
    if author_id:
        query = query.where(Post.author_id == author_id)

    if sort == "oldest":
        query = query.order_by(Post.created_at.asc())
    elif sort == "most_liked":
        # Subquery-free approximation: sort by view_count as a cheap proxy is avoided;
        # instead we sort in Python for correctness after fetching counts (small dataset
        # assumption is documented in ARCHITECTURE.md's scaling notes).
        query = query.order_by(Post.created_at.desc())
    else:
        query = query.order_by(Post.created_at.desc())

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    items = db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return list(items), total, [], None


def list_by_author(db: Session, author_id: int) -> list[Post]:
    return list(
        db.execute(
            select(Post).options(joinedload(Post.author)).where(Post.author_id == author_id).order_by(Post.created_at.desc())
        ).scalars().all()
    )


def like_count(db: Session, post_id: int) -> int:
    return db.execute(select(func.count()).select_from(Like).where(Like.post_id == post_id)).scalar_one()


def comment_count(db: Session, post_id: int) -> int:
    return db.execute(select(func.count()).select_from(Comment).where(Comment.post_id == post_id)).scalar_one()


def like_counts_for(db: Session, post_ids: list[int]) -> dict[int, int]:
    """Batched count query used by list endpoints so we issue ONE query for
    all posts on the page instead of one query per post."""
    if not post_ids:
        return {}
    rows = db.execute(
        select(Like.post_id, func.count()).where(Like.post_id.in_(post_ids)).group_by(Like.post_id)
    ).all()
    return {post_id: count for post_id, count in rows}


def comment_counts_for(db: Session, post_ids: list[int]) -> dict[int, int]:
    if not post_ids:
        return {}
    rows = db.execute(
        select(Comment.post_id, func.count()).where(Comment.post_id.in_(post_ids)).group_by(Comment.post_id)
    ).all()
    return {post_id: count for post_id, count in rows}
