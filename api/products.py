"""
Products API endpoints for Vercel Serverless
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone

from backend.products.models import Product
from backend.businesses.models import Business, User


def get_request_body(request):
    """Parse JSON body from request"""
    try:
        return json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return {}


def get_user_from_token(request):
    """Extract user from JWT token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        from django.conf import settings
        from decouple import config
        
        secret_key = config('SECRET_KEY', default='django-insecure-change-this-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        return User.objects.get(id=user_id)
    except Exception:
        return None


def require_auth(f):
    """Decorator to require authentication"""
    def wrapper(request, *args, **kwargs):
        user = get_user_from_token(request)
        
        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        request.user = user
        return f(request, *args, **kwargs)
    
    return wrapper


def check_permission(user, permission):
    """Check if user has a specific permission based on role"""
    if user.is_superuser:
        return True
    
    role_permissions = {
        'admin': ['create_product', 'edit_product', 'delete_product', 'approve_product', 'view_product'],
        'editor': ['create_product', 'edit_product', 'view_product'],
        'approver': ['approve_product', 'view_product'],
        'viewer': ['view_product'],
    }
    
    return permission in role_permissions.get(user.role, [])


def get_products_queryset(user, is_public=False):
    """Get filtered queryset based on user permissions"""
    if is_public:
        return Product.objects.filter(status='approved')
    
    if user.is_superuser:
        return Product.objects.all()
    
    return Product.objects.filter(
        Q(business__owner=user) | 
        Q(business=user.business)
    ).distinct()


def handler(request, action=''):
    """
    Handle product requests
    """
    # Parse action path
    action = action.rstrip('/')
    
    # Check for public listing
    is_public = request.query_params.get('public') == 'true'
    
    # Get user if authenticated
    user = get_user_from_token(request)
    
    if request.method == 'GET':
        # Public listing
        if is_public:
            return list_products(request, is_public=True)
        
        # Authenticated requests
        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check if this is a detail request (e.g., /api/products/1/)
        if action and action != 'products':
            try:
                product_id = int(action.split('/')[0])
                return get_product(request, product_id)
            except (ValueError, IndexError):
                return JsonResponse({'error': 'Invalid product ID'}, status=404)
        
        return list_products(request)
    
    elif request.method == 'POST':
        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not check_permission(user, 'create_product'):
            return JsonResponse({'error': "You don't have permission to create products"}, status=403)
        
        return create_product(request)
    
    elif request.method in ['PUT', 'PATCH']:
        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not check_permission(user, 'edit_product'):
            return JsonResponse({'error': "You don't have permission to edit products"}, status=403)
        
        try:
            product_id = int(action.split('/')[0])
            return update_product(request, product_id)
        except (ValueError, IndexError):
            return JsonResponse({'error': 'Invalid product ID'}, status=404)
    
    elif request.method == 'DELETE':
        if user is None:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        if not check_permission(user, 'delete_product'):
            return JsonResponse({'error': "You don't have permission to delete products"}, status=403)
        
        try:
            product_id = int(action.split('/')[0])
            return delete_product(request, product_id)
        except (ValueError, IndexError):
            return JsonResponse({'error': 'Invalid product ID'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def list_products(request, is_public=False):
    """List all products"""
    user = get_user_from_token(request) if not is_public else None
    
    queryset = get_products_queryset(user, is_public) if user else Product.objects.filter(status='approved')
    
    # Apply filters
    status_filter = request.query_params.get('status')
    if status_filter and not is_public:
        queryset = queryset.filter(status=status_filter)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    products = queryset[start:end]
    
    return JsonResponse({
        'count': queryset.count(),
        'page': page,
        'page_size': page_size,
        'results': [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': str(p.price),
                'status': p.status,
                'business': p.business.name if p.business else None,
                'created_at': p.created_at.isoformat() if p.created_at else None,
                'updated_at': p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in products
        ]
    })


def get_product(request, product_id):
    """Get a single product"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Check access for non-public products
    user = get_user_from_token(request)
    if product.status != 'approved' and user:
        has_access = (
            user.is_superuser or
            product.business.owner == user or
            product.business == user.business
        )
        if not has_access:
            return JsonResponse({'error': 'Access denied'}, status=403)
    elif product.status != 'approved':
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'status': product.status,
        'business': {
            'id': product.business.id,
            'name': product.business.name,
        } if product.business else None,
        'created_by': product.created_by.email if product.created_by else None,
        'approved_by': product.approved_by.email if product.approved_by else None,
        'approved_at': product.approved_at.isoformat() if product.approved_at else None,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None,
    })


@csrf_exempt
@require_auth
def create_product(request):
    """Create a new product"""
    data = get_request_body(request)
    
    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    
    if not name or price is None:
        return JsonResponse({'error': 'Name and price are required'}, status=400)
    
    # Get business
    business_id = data.get('business')
    if business_id:
        try:
            business = Business.objects.get(id=business_id)
            # Check access
            if not request.user.is_superuser and business.owner != request.user and business != request.user.business:
                return JsonResponse({'error': 'Access denied to this business'}, status=403)
        except Business.DoesNotExist:
            return JsonResponse({'error': 'Business not found'}, status=404)
    else:
        business = request.user.business
    
    if not business:
        return JsonResponse({'error': 'No business associated with user'}, status=400)
    
    product = Product.objects.create(
        name=name,
        description=description,
        price=price,
        business=business,
        created_by=request.user,
        status='draft'
    )
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'status': product.status,
        'created_at': product.created_at.isoformat() if product.created_at else None,
    }, status=201)


@csrf_exempt
@require_auth
def update_product(request, product_id):
    """Update a product"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Check access
    if not request.user.is_superuser and product.business.owner != request.user and product.business != request.user.business:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    data = get_request_body(request)
    
    # Update fields
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'status' in data and request.user.is_superuser:
        product.status = data['status']
    
    product.save()
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'status': product.status,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None,
    })


@csrf_exempt
@require_auth
def delete_product(request, product_id):
    """Delete a product"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Check access
    if not request.user.is_superuser and product.business.owner != request.user and product.business != request.user.business:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    product.delete()
    
    return JsonResponse({'message': 'Product deleted successfully'})


@csrf_exempt
@require_auth
def approve_product(request, product_id):
    """Approve a product"""
    if not check_permission(request.user, 'approve_product'):
        return JsonResponse({'error': "You don't have permission to approve products"}, status=403)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    if product.status == 'approved':
        return JsonResponse({'error': 'Product is already approved'}, status=400)
    
    if product.status != 'pending_approval':
        return JsonResponse({'error': 'Only products pending approval can be approved'}, status=400)
    
    product.status = 'approved'
    product.approved_by = request.user
    product.approved_at = timezone.now()
    product.save()
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'status': product.status,
        'approved_by': product.approved_by.email,
        'approved_at': product.approved_at.isoformat(),
    })


@csrf_exempt
@require_auth
def submit_for_approval(request, product_id):
    """Submit a product for approval"""
    if not check_permission(request.user, 'edit_product'):
        return JsonResponse({'error': "You don't have permission to submit products for approval"}, status=403)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    if product.status != 'draft':
        return JsonResponse({'error': 'Only draft products can be submitted for approval'}, status=400)
    
    product.status = 'pending_approval'
    product.save()
    
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'status': product.status,
    })
