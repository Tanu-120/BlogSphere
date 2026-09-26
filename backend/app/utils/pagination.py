"""Shared page / page_size bounds for list endpoints."""
from app.config import get_settings

settings = get_settings()


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), settings.MAX_PAGE_SIZE)
    return page, page_size


def total_pages(total: int, page_size: int) -> int:
    return max(1, (total + page_size - 1) // page_size)
