"""
URL Configuration for Product Marketplace API
=============================================

This module defines the main URL routing for the Django application.
It serves as the central hub that directs incoming HTTP requests to 
the appropriate view functions based on URL patterns.

URL Structure:
- /admin/           - Django admin interface for superuser management
- /api/auth/        - Authentication endpoints (login, register, token refresh)
- /api/products/    - Product CRUD operations with role-based permissions
- /api/chatbot/     - AI chatbot query and history endpoints

Security Features:
- All API endpoints require authentication (configured in settings.py)
- Role-based access control implemented at the view level
- CORS configured for frontend integration
- Rate limiting applied to prevent abuse

API Documentation:
- Swagger/OpenAPI docs available at /api/schema/swagger-ui/
- ReDoc documentation at /api/schema/redoc/
- Raw OpenAPI schema at /api/schema/

For detailed endpoint documentation, see the API section in README.md
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Main URL patterns for the application
urlpatterns = [
    # Django Admin Interface
    # Provides web-based administration for superusers
    # Access: http://localhost:8000/admin/
    path('admin/', admin.site.urls),
    
    # Authentication API Endpoints
    # Handles user registration, login, token refresh, and user management
    # Includes: POST /api/auth/register/, POST /api/auth/login/, etc.
    path('api/auth/', include('businesses.urls')),
    
    # Product Management API Endpoints  
    # CRUD operations for products with approval workflow
    # Includes: GET/POST /api/products/, PUT/DELETE /api/products/{id}/, etc.
    path('api/products/', include('products.urls')),
    
    # AI Chatbot API Endpoints
    # Natural language queries about products using OpenAI
    # Includes: POST /api/chatbot/query/, GET /api/chatbot/history/
    path('api/chatbot/', include('chatbot.urls')),
    
    # API Documentation Endpoints (drf-spectacular)
    # Provides interactive API documentation for developers
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
