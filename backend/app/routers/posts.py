"""
Public + author-facing endpoints for blog posts.
- Anyone (no auth) can browse/read published posts.
- Authenticated users can create/manage their OWN posts.
- Admins can moderate any post.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_current_user_optional
from app.core.permissions import ensure_author_can_see_draft, ensure_owner_or_admin
from app.database import get_db
from app.models.post import PostStatus
from app.models.user import User
from app.repositories import post_repository
from app.schemas.post import PostOut, PaginatedPosts, PostUpdate, AIGenerateResponse
from app.services import post_service
from app.services.ai_service import generate_summary_and_tags
from app.services.serializers import post_to_out, posts_to_list_items
from app.utils.cache import cached
from app.utils.file_upload import save_upload
from app.utils.pagination import normalize_pagination, total_pages

router = APIRouter(prefix="/api/posts", tags=["posts"])


@cached(ttl_seconds=30)
def _cached_list(db: Session, page: int, page_size: int, search, tag, author_id, sort):
    return post_repository.list_published(db, page, page_size, search, tag, author_id, sort)


@router.get("", response_model=PaginatedPosts)
def list_posts(
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    tag: str | None = None,
    author_id: int | None = None,
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    """Public. Search, tag, author, sort, and page are all query parameters."""
    page, page_size = normalize_pagination(page, page_size)
    cache_key = f"posts:list:{page}:{page_size}:{search}:{tag}:{author_id}:{sort}"
    posts, total, models, llm_name = _cached_list(db, page, page_size, search, tag, author_id, sort, cache_key=cache_key)
    return PaginatedPosts(
        items=posts_to_list_items(db, posts),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages(total, page_size),
        search_models=models,
        llm=llm_name,
    )


@router.get("/{slug}", response_model=PostOut)
def get_post(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
    x_reader: str | None = Header(default=None),
):
    """Public endpoint. Published posts are visible to everyone. A draft is visible only to its author."""
    post = post_repository.get_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    ensure_author_can_see_draft(current_user, post)
    post_service.record_view(db, post, current_user, x_reader)
    db.refresh(post)
    return post_to_out(db, post, current_user)


@router.post("", response_model=PostOut, status_code=201)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str | None = Form(None),
    tags: str | None = Form(None),
    status_: PostStatus = Form(PostStatus.DRAFT, alias="status"),
    cover_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Requires authentication. Optional cover image is multipart form data."""
    cover_url = await save_upload(cover_image) if cover_image else None
    from app.schemas.post import PostCreate
    payload = PostCreate(title=title, content=content, excerpt=excerpt, tags=tags, status=status_)
    post = post_service.create_post(db, current_user, payload, cover_url)
    return post_to_out(db, post, current_user)


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The author may update their post. An admin may update a published post, not a draft."""
    post = post_service.get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    ensure_owner_or_admin(current_user, post.author_id, action="edit this post")
    post = post_service.update_post(db, post, payload)
    return post_to_out(db, post, current_user)


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """The author may delete their post. An admin may delete a published post, not a draft."""
    post = post_service.get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    ensure_owner_or_admin(current_user, post.author_id, action="delete this post")
    post_service.delete_post(db, post)


@router.post("/{post_id}/ai/generate", response_model=AIGenerateResponse)
async def generate_ai_summary(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """AI topic: owner-triggered summary + tag suggestion for their own post,
    using a pluggable LLM provider with graceful local fallback."""
    post = post_service.get_post_or_404(db, post_id)
    ensure_author_can_see_draft(current_user, post)
    ensure_owner_or_admin(current_user, post.author_id, action="generate AI content for this post")

    summary, tags, source = await generate_summary_and_tags(post.title, post.content)
    post.ai_summary = summary
    post.ai_tags = tags
    db.commit()
    return AIGenerateResponse(ai_summary=summary, ai_tags=tags, source=source)
