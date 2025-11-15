from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED
)

# Rate limit configurations
RATE_LIMITS = {
    "public_default": "100/minute",      # Public endpoints
    "auth": "5/minute",                  # Login/register
    "admin": "200/minute",               # Admin endpoints (authenticated)
    "webhooks": "1000/minute",           # Stripe webhooks
    "images": "20/minute"                # Image uploads
}
