from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class CampusConnectException(Exception):
    """Base exception for CampusConnect"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EntityNotFoundException(CampusConnectException):
    """Entity not found in database"""
    def __init__(self, entity_type: str, entity_id: int):
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message, status_code=404)

class UnauthorizedException(CampusConnectException):
    """User is not authorized"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=401)

class SubscriptionException(CampusConnectException):
    """Subscription-related error"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


async def campusconnect_exception_handler(request: Request, exc: CampusConnectException):
    """Handle custom CampusConnect exceptions"""
    logger.error(f"CampusConnect Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with better messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": errors
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database error occurred",
            "message": "An internal error occurred. Please try again later."
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please contact support."
        }
    )
