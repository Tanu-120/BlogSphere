import re
import uuid


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = "post"
    # Append a short random suffix to keep slugs unique even for duplicate titles.
    return f"{slug}-{uuid.uuid4().hex[:6]}"
