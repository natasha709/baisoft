"""
Custom Middleware for BAISoft Product Marketplace

This module provides custom middleware for:
- API request/response logging
- Error handling and formatting
- Performance monitoring
- Request ID tracking
"""

import logging
import time
import uuid
from typing import Callable

from django.http import JsonResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django')


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that adds a unique request ID to each request.
    This is useful for tracing requests through logs.
    """
    
    HEADER_NAME = 'X-Request-ID'
    
    def process_request(self, request: HttpRequest):
        # Check if request ID is provided in headers, otherwise generate one
        request.request_id = request.META.get(
            f'HTTP_{self.HEADER_NAME.upper().replace("-", "_")}',
            str(uuid.uuid4())
        )


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs API requests and responses.
    """
    
    # Paths to exclude from logging
    EXCLUDE_PATHS = ['/health/', '/status/']
    
    def process_request(self, request: HttpRequest):
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return None
            
        request.start_time = time.time()
        
        logger.debug(
            f"API Request: {request.method} {request.path}",
            extra={
                'request_id': getattr(request, 'request_id', 'N/A'),
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': self.get_client_ip(request),
            }
        )
        
        return None
    
    def process_response(self, request: HttpRequest, response):
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return response
        
        # Calculate request duration
        duration_ms = 0
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
        
        # Log response
        log_level = logger.warning if response.status_code >= 400 else logger.info
        
        log_level(
            f"API Response: {request.method} {request.path} - "
            f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms",
            extra={
                'request_id': getattr(request, 'request_id', 'N/A'),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
            }
        )
        
        # Add request ID to response headers
        response['X-Request-ID'] = getattr(request, 'request_id', 'N/A')
        
        return response
    
    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the chain (client IP)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip


class APIErrorHandlerMiddleware(MiddlewareMixin):
    """
    Middleware that catches unhandled exceptions and returns JSON responses.
    This ensures consistent error format across the API.
    """
    
    # Paths to exclude from error handling (let Django handle them)
    EXCLUDE_PATHS = ['/admin/']
    
    def process_exception(self, request: HttpRequest, exception: Exception):
        # Skip for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return None
        
        # Import here to avoid circular imports
        from django.core.exceptions import PermissionDenied, ValidationError
        from django.contrib.auth.decorators import login_required
        
        # Log the exception
        logger.exception(
            f"Unhandled exception: {str(exception)}",
            extra={
                'request_id': getattr(request, 'request_id', 'N/A'),
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'exception_type': type(exception).__name__,
            }
        )
        
        # Handle specific exception types
        if isinstance(exception, PermissionDenied):
            return JsonResponse(
                {
                    'error': 'Permission denied',
                    'message': str(exception),
                    'code': 'PERMISSION_DENIED',
                },
                status=403
            )
        
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {
                    'error': 'Validation error',
                    'message': str(exception),
                    'code': 'VALIDATION_ERROR',
                },
                status=400
            )
        
        # Handle generic exceptions
        # In production, don't expose internal error details
        from django.conf import settings
        
        if settings.DEBUG:
            error_detail = str(exception)
        else:
            error_detail = "An internal error occurred. Please contact support if this persists."
        
        return JsonResponse(
            {
                'error': 'Internal server error',
                'message': error_detail,
                'code': 'INTERNAL_ERROR',
                'request_id': getattr(request, 'request_id', 'N/A'),
            },
            status=500
        )


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that adds security headers to responses.
    """
    
    def process_response(self, request: HttpRequest, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.openai.com"
        )
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options (already handled by Django's XFrameOptionsMiddleware)
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection (legacy but still useful)
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            'accelerometer=(), '
            'camera=(), '
            'geolocation=(), '
            'gyroscope=(), '
            'magnetometer=(), '
            'microphone=(), '
            'payment=(), '
            'usb=()'
        )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to add rate limit headers to responses.
    Works with django-ratelimit.
    """
    
    def process_response(self, request: HttpRequest, response):
        # Add rate limit headers if available
        if hasattr(request, 'ratelimit_used'):
            response['X-RateLimit-Limit'] = str(getattr(request, 'ratelimit_limit', ''))
            response['X-RateLimit-Remaining'] = str(getattr(request, 'ratelimit_remaining', 0))
            response['X-RateLimit-Reset'] = str(getattr(request, 'ratelimit_reset', ''))
        
        return response
