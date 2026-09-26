"""CSV export of the signed-in user's own posts."""
import csv
import io

from app.models.post import Post


def posts_to_csv(posts: list[Post]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "title", "slug", "status", "tags", "views", "created_at"])
    for p in posts:
        writer.writerow([p.id, p.title, p.slug, p.status.value, p.tags or "", p.view_count, p.created_at.isoformat()])
    return buffer.getvalue()
