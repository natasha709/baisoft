"""
Vercel Serverless API Handler
Django-compatible API endpoints running on Vercel's Python runtime
"""

import os
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs

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


class VercelRequest:
    """
    Wrapper class to convert Vercel request to Django-like request
    """
    def __init__(self, vercel_request):
        self.vercel_request = vercel_request
        self.path = vercel_request.path
        self.method = vercel_request.method
        self.headers = dict(vercel_request.headers) if hasattr(vercel_request, 'headers') else {}
        self.body = vercel_request.body if hasattr(vercel_request, 'body') else b''
        
        # Parse query parameters
        query_string = vercel_request.url.split('?')[1] if '?' in vercel_request.url else ''
        self.query_params = {k: v[0] if len(v) == 1 else v 
                            for k, v in parse_qs(query_string).items()}
    
    def __getattr__(self, name):
        # Delegate to the underlying Vercel request
        return getattr(self.vercel_request, name)


def handler(vercel_request, vercel_response):
    """
    Main request handler for Vercel serverless functions
    """
    try:
        # Convert Vercel request to Django-like request
        request = VercelRequest(vercel_request)
        
        # Parse the request path
        path_info = request.path.strip('/')
        
        # Route to appropriate handler
        if path_info.startswith('api/auth/'):
            response = auth.handle(request, path_info.replace('api/auth/', ''))
        elif path_info.startswith('api/products/'):
            response = products.handle(request, path_info.replace('api/products/', ''))
        elif path_info.startswith('api/chatbot/'):
            response = chatbot.handle(request, path_info.replace('api/chatbot/', ''))
        elif path_info == 'api' or path_info == 'api/':
            response = JsonResponse({
                'message': 'BAISoft Product Marketplace API',
                'version': '1.0.0',
                'endpoints': {
                    'auth': '/api/auth/',
                    'products': '/api/products/',
                    'chatbot': '/api/chatbot/'
                }
            })
        else:
            response = JsonResponse({'error': 'Not found'}, status=404)
        
        # Convert Django response to Vercel response
        vercel_response.status = response.status_code
        for header, value in response.items():
            vercel_response.header(header, value)
        
        vercel_response.send(response.content.decode('utf-8'))
        return vercel_response
        
    except Exception as e:
        # Handle any errors
        error_response = JsonResponse({'error': str(e)}, status=500)
        vercel_response.status = error_response.status_code
        vercel_response.send(error_response.content.decode('utf-8'))
        return vercel_response


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
