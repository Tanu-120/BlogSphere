"""
Cover image uploads: type and size checks, random filenames, local storage.
Stores locally under app/uploads/ and is served at /uploads/<filename>.
Swapping to S3-compatible object storage only requires changing `save_upload`.
"""
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from app.config import get_settings

settings = get_settings()
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def save_upload(file: UploadFile) -> str:
    if file.content_type not in settings.allowed_image_types_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # Stream to disk in chunks rather than loading the whole file into memory.
    ext = Path(file.filename or "").suffix or ".bin"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    destination = UPLOAD_DIR / safe_name

    size = 0
    with destination.open("wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                out_file.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
                )
            out_file.write(chunk)

    return f"/uploads/{safe_name}"
