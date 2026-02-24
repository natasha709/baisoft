"""
Custom middleware for BAISoft Product Marketplace

This module provides custom middleware for request logging,
error handling, and security headers.
"""

import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that adds a unique request ID to each request.
    This helps with tracking requests across logs.
    """
    
    def process_request(self, request):
        # Generate or retrieve request ID
        request.id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        return None
    
    def process_response(self, request, response):
        # Add request ID to response headers
        response['X-Request-ID'] = getattr(request, 'id', 'unknown')
        return response


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs API requests and responses.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        logger.info(f"API Request: {request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"Status: {response.status_code} Duration: {duration:.3f}s"
            )
        return response


class APIErrorHandlerMiddleware(MiddlewareMixin):
    """
    Middleware that handles exceptions and returns proper JSON responses.
    """
    
    def process_exception(self, request, exception):
        logger.error(
            f"API Error: {request.method} {request.path} "
            f"Error: {str(exception)}",
            exc_info=True
        )
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that adds security headers to responses.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
