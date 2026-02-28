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

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/auth/', include('businesses.urls')),

    path('api/products/', include('products.urls')),

    path('api/chatbot/', include('chatbot.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
