"""
Vercel Serverless API Handler
Django-compatible API endpoints running on Vercel's Python runtime
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.http import JsonResponse
from django.urls import path

# Import views
from api import auth, products, chatbot

def handler(request, path_param=None):
    """
    Main request handler for Vercel serverless functions
    """
    # Parse the request path
    path_info = request.path.strip('/')
    
    # Route to appropriate handler
    if path_info.startswith('api/auth/'):
        return auth.handle(request, path_info.replace('api/auth/', ''))
    elif path_info.startswith('api/products/'):
        return products.handle(request, path_info.replace('api/products/', ''))
    elif path_info.startswith('api/chatbot/'):
        return chatbot.handle(request, path_info.replace('api/chatbot/', ''))
    elif path_info == 'api' or path_info == 'api/':
        return JsonResponse({
            'message': 'BAISoft Product Marketplace API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/',
                'products': '/api/products/',
                'chatbot': '/api/chatbot/'
            }
        })
    else:
        return JsonResponse({'error': 'Not found'}, status=404)


# URL patterns for Vercel
urlpatterns = [
    path('api/auth/<str:action>', auth.handler),
    path('api/auth/', auth.handler),
    path('api/products/<path:action>', products.handler),
    path('api/products/', products.handler),
    path('api/chatbot/<str:action>', chatbot.handler),
    path('api/chatbot/', chatbot.handler),
    path('api/', lambda r: JsonResponse({'status': 'ok'})),
]
