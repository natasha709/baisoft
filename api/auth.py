"""
Authentication API endpoints for Vercel Serverless
"""

import json
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone

User = get_user_model()


def get_request_body(request):
    """Parse JSON body from request"""
    try:
        return json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return {}


def require_auth(f):
    """Decorator to require authentication"""
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        token = auth_header.replace('Bearer ', '')
        
        try:
            from django.conf import settings
            from decouple import config
            
            secret_key = config('SECRET_KEY', default='django-insecure-change-this-in-production')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            user_id = payload.get('user_id')
            if not user_id:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            
            user = User.objects.get(id=user_id)
            request.user = user
            
            return f(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
    
    return wrapper


def handler(request, action=''):
    """
    Handle authentication requests
    """
    # Remove trailing slashes
    action = action.rstrip('/')
    
    if request.method == 'POST':
        if action in ['login', '']:
            return login(request)
        elif action == 'register':
            return register(request)
        elif action == 'logout':
            return logout(request)
        elif action == 'token/refresh':
            return refresh_token(request)
        elif action == 'change-password':
            return change_password(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=404)
    
    elif request.method == 'GET':
        if action == 'me':
            return current_user(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def login(request):
    """User login endpoint"""
    data = get_request_body(request)
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)
    
    user = authenticate(email=email, password=password)
    
    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return JsonResponse({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'business': user.business_id,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@csrf_exempt
def register(request):
    """User registration endpoint"""
    data = get_request_body(request)
    
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    business_name = data.get('business_name', '')
    
    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already registered'}, status=400)
    
    from backend.businesses.models import Business
    
    # Create business if provided
    business = None
    if business_name:
        business = Business.objects.create(name=business_name)
    
    # Create user
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        business=business,
        role='admin' if business else 'viewer'
    )
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return JsonResponse({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'business': user.business_id,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=201)


@csrf_exempt
@require_auth
def logout(request):
    """User logout endpoint - blacklist the token"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    try:
        from decouple import config
        secret_key = config('SECRET_KEY', default='django-insecure-change-this-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Blacklist the token
        outstanding_token = OutstandingToken.objects.filter(
            user_id=payload.get('user_id'),
            token=token
        ).first()
        
        if outstanding_token:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
        
        return JsonResponse({'message': 'Logged out successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Logged out successfully'})


@csrf_exempt
def refresh_token(request):
    """Refresh access token"""
    data = get_request_body(request)
    
    refresh_token_str = data.get('refresh')
    
    if not refresh_token_str:
        return JsonResponse({'error': 'Refresh token is required'}, status=400)
    
    try:
        refresh = RefreshToken(refresh_token_str)
        
        return JsonResponse({
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })
    except Exception as e:
        return JsonResponse({'error': 'Invalid refresh token'}, status=401)


@csrf_exempt
@require_auth
def current_user(request):
    """Get current user info"""
    user = request.user
    
    return JsonResponse({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'business': user.business_id,
    })


@csrf_exempt
@require_auth
def change_password(request):
    """Change user password"""
    data = get_request_body(request)
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return JsonResponse({'error': 'Old and new passwords are required'}, status=400)
    
    user = request.user
    
    if not user.check_password(old_password):
        return JsonResponse({'error': 'Current password is incorrect'}, status=400)
    
    # Check if temporary password has expired
    if user.temporary_password_expires and timezone.now() > user.temporary_password_expires:
        return JsonResponse({'error': 'Temporary password has expired'}, status=400)
    
    user.set_password(new_password)
    user.password_change_required = False
    user.temporary_password_expires = None
    user.save()
    
    return JsonResponse({'message': 'Password changed successfully'})
