"""Assembles API response objects that combine multiple tables
(post + like_count + comment_count + liked_by_me) without leaking
SQLAlchemy internals into the routers."""
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.like import Like
from app.models.user import User
from app.repositories import post_repository
from app.schemas.post import PostOut, PostListItem


def post_to_out(db: Session, post: Post, current_user: User | None) -> PostOut:
    liked_by_me = False
    if current_user:
        liked_by_me = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first() is not None
    return PostOut(
        **{k: getattr(post, k) for k in [
            "id", "title", "slug", "content", "excerpt", "cover_image_url", "tags",
            "status", "ai_summary", "ai_tags", "view_count", "author", "created_at", "updated_at",
        ]},
        like_count=post_repository.like_count(db, post.id),
        comment_count=post_repository.comment_count(db, post.id),
        liked_by_me=liked_by_me,
    )


def posts_to_list_items(db: Session, posts: list[Post]) -> list[PostListItem]:
    """Serializes a whole page of posts using two batched count queries
    (see post_repository.like_counts_for/comment_counts_for) instead of
    2*N queries — the N+1 fix for the public feed."""
    post_ids = [p.id for p in posts]
    likes = post_repository.like_counts_for(db, post_ids)
    comments = post_repository.comment_counts_for(db, post_ids)
    return [
        PostListItem(
            **{k: getattr(post, k) for k in [
                "id", "title", "slug", "excerpt", "cover_image_url", "tags", "status", "author", "created_at",
            ]},
            like_count=likes.get(post.id, 0),
            comment_count=comments.get(post.id, 0),
        )
        for post in posts
    ]
