import os
import logging.config
from pathlib import Path
from datetime import timedelta
from decouple import config

# Import custom logging configuration
from config.logging import configure_logging

# --------------------------------------------------
# BASE CONFIG
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS is parsed from a comma-separated env var for easier deployment config.
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,testserver',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    # Default Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',  # API Documentation

    # Local Apps
    'businesses',
    'products',
    'chatbot',
]

# --------------------------------------------------
# MIDDLEWARE (Professional Enhancement)
# --------------------------------------------------

MIDDLEWARE = [
    # Security middleware first
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    
    # Django authentication middleware must come BEFORE custom middleware
    # that accesses request.user (like APILoggingMiddleware and APIErrorHandlerMiddleware)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware for logging, error handling, etc.
    'config.middleware.RequestIDMiddleware',
    'config.middleware.APILoggingMiddleware',
    'config.middleware.APIErrorHandlerMiddleware',
    'config.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --------------------------------------------------
# AUTH
# --------------------------------------------------

AUTH_USER_MODEL = 'businesses.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --------------------------------------------------
# DJANGO REST FRAMEWORK (Professional Enhancement)
# --------------------------------------------------

REST_FRAMEWORK = {
    # Use JWT globally so API endpoints require authenticated access by default.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # API Schema (drf-spectacular)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Exception handler for consistent error responses
    'EXCEPTION_HANDLER': 'drf_spectacular.contrib.exception_handler.get_exception_handler',
    
    # Throttling (built-in Django REST framework throttling)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'chatbot': '50/hour',  # Chatbot specific rate limit
    },
}

# --------------------------------------------------
# SPECTACULAR (API Documentation)
# --------------------------------------------------

SPECTACULAR_SETTINGS = {
    'TITLE': 'BAISoft Product Marketplace API',
    'DESCRIPTION': '''
## Overview
Internal Product Management System with Role-Based Access Control

### Features
- JWT Authentication with role-based permissions
- Product CRUD with approval workflow
- Business management
- AI-powered chatbot for product queries

### User Roles
| Role | Permissions |
|------|-------------|
| Admin | Full access to all operations |
| Editor | Create and edit products |
| Approver | Review and approve products |
| Viewer | View products only |
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    
    # Security schemes
    'SECURITY': [
        {
            'Bearer': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    ],
}

# --------------------------------------------------
# JWT CONFIGURATION
# --------------------------------------------------

SIMPLE_JWT = {
    # Short-lived access tokens + refresh token rotation improves security posture.
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    
    # Token verification
    'VERIFYING_KEY': None,  # Uses SECRET_KEY for RS256
    'ALGORITHM': 'HS256',
}

# --------------------------------------------------
# CORS (Professional Enhancement)
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    # Frontend development origins.
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Add production origins here
]

# Additional CORS settings
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------
# SECURITY SETTINGS (Professional Enhancement)
# --------------------------------------------------

# HTTPS settings (enable in production)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session cookie settings
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 year in production
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
SECURE_CONTENT_TYPE_NOSNIFF = True

# X-Frame-Options (already handled by middleware, but keep for redundancy)
X_FRAME_OPTIONS = 'DENY'

# --------------------------------------------------
# RATE LIMITING (Professional Enhancement)
# --------------------------------------------------

RATELIMIT_USE_CACHE = 'default'
RATELIMIT_DEFAULT = '100/h'

# --------------------------------------------------
# CACHING (Professional Enhancement)
# --------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# --------------------------------------------------
# SENTRY (Error Tracking - Professional Enhancement)
# --------------------------------------------------

SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=0.1,
        
        # Profile notifs 100% of sampled transactions
        profiles_sample_rate=0.1,
        
        # Associate users with errors
        send_default_pii=True,
        
        # Environment
        environment='production' if not DEBUG else 'development',
        
        # Release tracking
        release=f'baisoft@{os.environ.get("VERSION", "1.0.0")}',
    )

# --------------------------------------------------
# OPENAI
# --------------------------------------------------

OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')

# --------------------------------------------------
# EMAIL CONFIGURATION
# --------------------------------------------------

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default='noreply@productmarketplace.com'
)

# --------------------------------------------------
# LOGGING CONFIGURATION (Professional Enhancement)
# --------------------------------------------------

# Initialize logging
configure_logging()
