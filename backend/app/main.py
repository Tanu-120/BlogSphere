"""
Application entrypoint: wires together middleware, routers, static file
serving for uploads, exception handling, DB table creation, and a simple
rate limiter, and a health check.
"""
import logging
import time
from collections import defaultdict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import Base, engine
import app.models  # noqa: F401  registers tables, including post_views, before create_all
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.routers import auth, posts, comments, likes, users, admin
from app.seed import seed_demo_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = get_settings()

# Create tables on startup. For a real production deploy this would be
# replaced by versioned Alembic migrations (the SQLAlchemy models here are
# already Alembic-compatible); create_all keeps `docker compose up`
# simple for local setup.
Base.metadata.create_all(bind=engine)
seed_demo_data()

app = FastAPI(
    title=settings.APP_NAME,
    description="A user-specific blog platform with auth, RBAC, comments, likes, file uploads and AI-assisted summaries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# --- Fixed-window rate limiter ---------------------------------------------
_request_log: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60
    _request_log[client_ip] = [t for t in _request_log[client_ip] if t > window_start]

    if len(_request_log[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again shortly."})

    _request_log[client_ip].append(now)
    return await call_next(request)


# --- Consistent error envelope ---------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


# --- Static files (uploaded cover images) -----------------------------------
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- Routers -----------------------------------------------------------------
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/", tags=["system"])
def root():
    return {
        "name": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
    }
