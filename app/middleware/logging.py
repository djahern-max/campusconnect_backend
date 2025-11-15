import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information"""
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get request info
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"📥 {method} {url} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            status = response.status_code
            if status >= 500:
                logger.error(f"❌ {method} {url} - {status} - {duration:.3f}s")
            elif status >= 400:
                logger.warning(f"⚠️  {method} {url} - {status} - {duration:.3f}s")
            else:
                logger.info(f"✅ {method} {url} - {status} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"💥 {method} {url} - ERROR: {str(e)} - {duration:.3f}s")
            raise
