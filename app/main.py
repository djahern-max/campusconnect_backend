from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.tasks.cleanup import start_scheduler
from app.core.rate_limit import limiter
from app.core.logging_config import logger
from app.core.config import settings
from app.middleware.logging import RequestLoggingMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute
from app.core.exceptions import (
    CampusConnectException,
    campusconnect_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.api.v1 import (
    institutions,
    scholarships,
    admin_auth,
    outreach,
    admin_profile,
    admin_images,
    admin_gallery,
    admin_videos,
    admin_extended_info,
    subscriptions,
    webhooks,
    institutions_data,
    admin_data,
)

app = FastAPI(
    title="CampusConnect API",
    description="B2B SaaS platform for institutions and scholarships",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Exception handlers
app.add_exception_handler(CampusConnectException, campusconnect_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(institutions.router, prefix="/api/v1")
app.include_router(scholarships.router, prefix="/api/v1")
app.include_router(admin_auth.router, prefix="/api/v1")
app.include_router(outreach.router, prefix="/api/v1")
app.include_router(admin_profile.router, prefix="/api/v1")
app.include_router(admin_images.router, prefix="/api/v1")
app.include_router(admin_gallery.router, prefix="/api/v1")
app.include_router(admin_videos.router, prefix="/api/v1")
app.include_router(admin_extended_info.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(institutions_data.router, prefix="/api/v1")
app.include_router(admin_data.router, prefix="/api/v1")


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {
        "message": "CampusConnect API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "institutions": "/api/v1/institutions",
            "scholarships": "/api/v1/scholarships",
            "admin_auth": "/api/v1/admin/auth",
            "admin_profile": "/api/v1/admin/profile",
            "admin_images": "/api/v1/admin/images",
            "admin_gallery": "/api/v1/admin/gallery",
            "admin_videos": "/api/v1/admin/videos",
            "admin_extended_info": "/api/v1/admin/extended-info",
            "subscriptions": "/api/v1/admin/subscriptions",
            "webhooks": "/api/v1/webhooks/stripe",
        },
    }


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {"status": "healthy", "version": "1.0.0"}


# COMBINE BOTH STARTUP EVENTS INTO ONE
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 CampusConnect API starting up...")
    logger.info(f"📊 Database: {settings.DATABASE_URL[:30]}...")
    logger.info("🛡️  Rate limiting enabled")
    logger.info("📝 Request logging enabled")
    logger.info("🖼️  Gallery management enabled")
    logger.info("🎥 Video management enabled")
    logger.info("📄 Extended info enabled")

    # Start the scheduler for invitation cleanup
    start_scheduler()
    logger.info("⏰ Invitation cleanup scheduler started")

    logger.info("✅ All systems ready!")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 CampusConnect API shutting down...")


@app.get("/routes-simple", response_class=PlainTextResponse)
async def get_routes_simple():
    """
    Returns a concise list of all routes with their paths and methods.
    """
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            routes.append(f"{methods}: {route.path}")

    return "\n".join(routes)
