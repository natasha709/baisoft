"""
Chatbot API endpoints for Vercel Serverless
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

from backend.chatbot.models import ChatMessage
from backend.products.models import Product
from backend.businesses.models import User


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


def handler(request, action=''):
    """
    Handle chatbot requests
    """
    # Parse action path
    action = action.rstrip('/')
    
    if request.method == 'GET':
        # Get chat history
        if action == 'history' or action == '':
            return get_chat_history(request)
        return JsonResponse({'error': 'Invalid action'}, status=404)
    
    elif request.method == 'POST':
        if action == 'query':
            return chat_query(request)
        return JsonResponse({'error': 'Invalid action'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@require_auth
def chat_query(request):
    """Process a chat query and return AI response"""
    data = get_request_body(request)
    
    user_message = data.get('message')
    
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    
    # Get approved products for context
    products = Product.objects.filter(status='approved')
    
    # Business-scoped for non-superusers
    if not request.user.is_superuser and getattr(request.user, 'business_id', None):
        products = products.filter(business=request.user.business)
    else:
        products = products.all()
    
    # Get AI response
    try:
        ai_response = get_ai_response(user_message, products, request.user)
    except Exception as e:
        return JsonResponse({'error': f'AI service error: {str(e)}'}, status=500)
    
    # Save chat message
    chat_message = ChatMessage.objects.create(
        user=request.user,
        user_message=user_message,
        ai_response=ai_response
    )
    
    return JsonResponse({
        'message': user_message,
        'response': ai_response,
        'id': chat_message.id
    })


@require_auth
def get_chat_history(request):
    """Get chat history for the current user"""
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    messages = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[start:end]
    
    return JsonResponse({
        'count': ChatMessage.objects.filter(user=request.user).count(),
        'page': page,
        'page_size': page_size,
        'results': [
            {
                'id': msg.id,
                'user_message': msg.user_message,
                'ai_response': msg.ai_response,
                'created_at': msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]
    })


def get_ai_response(user_message, products, user):
    """
    Get AI response using OpenAI API with product context
    """
    import re
    from decouple import config
    from openai import OpenAI
    
    openai_api_key = config('OPENAI_API_KEY', default='')
    
    # Build product context
    product_list = []
    if products:
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'business': product.business.name if product.business else 'Unknown',
            })
    
    # If no API key, use local product search
    if not openai_api_key:
        return handle_local_product_query(user_message, product_list, user)
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        model = config('OPENAI_MODEL', default='gpt-3.5-turbo')
        
        # Handle purchase-related queries
        if is_purchase_query(user_message):
            return handle_purchase_query(user_message, product_list, user)
        
        # Check if this is a product search query
        if is_product_search(user_message) or is_specific_product_query(user_message):
            matching_products = search_products(user_message, product_list)
            if matching_products:
                return generate_detailed_product_response(matching_products, user_message)
            else:
                search_term = extract_search_terms(user_message)[0] if extract_search_terms(user_message) else "that term"
                return f"🔍 I couldn't find any products matching '{search_term}'.\n\n{generate_product_listing_response(product_list)}"
        
        # Check if it's a general product listing query
        if is_product_query(user_message):
            return generate_product_listing_response(product_list)
        
        # For other queries, use OpenAI
        system_prompt = f"""You are a helpful AI assistant for a product marketplace.
Current catalog status: {len(product_list)} products available

Product Catalog:
{format_products_for_prompt(product_list)}"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7,
            timeout=10
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fall back to local product handling
        return handle_local_product_query(user_message, product_list, user)


def handle_local_product_query(user_message, products, user):
    """Handle product queries locally without using OpenAI"""
    product_list = list(products)
    
    # Try to find direct product match
    direct_product_match = find_direct_product_match(user_message, product_list)
    if direct_product_match:
        return generate_detailed_product_response([direct_product_match], user_message)
    
    # Check for specific product queries
    if is_specific_product_query(user_message) or is_product_search(user_message):
        matching_products = search_products(user_message, product_list)
        if matching_products:
            return generate_detailed_product_response(matching_products, user_message)
        else:
            search_term = extract_search_terms(user_message)[0] if extract_search_terms(user_message) else "that"
            return f"🔍 I couldn't find any products matching '{search_term}'.\n\n{generate_product_listing_response(product_list)}"
    
    # Check for purchase queries
    if is_purchase_query(user_message):
        return handle_purchase_query(user_message, product_list, user)
    
    # Default to product listing
    return generate_product_listing_response(product_list)


def find_direct_product_match(query, products):
    """Find if the query directly mentions a product name"""
    if not products:
        return None
    
    query_lower = query.lower()
    prefixes = ['tell me about', 'what about', 'how about', 'info on', 'details on', 'about']
    
    cleaned_query = query_lower
    for prefix in prefixes:
        if cleaned_query.startswith(prefix):
            cleaned_query = cleaned_query[len(prefix):]
            break
    
    cleaned_query = cleaned_query.strip()
    
    for product in products:
        product_name_lower = product['name'].lower()
        if cleaned_query == product_name_lower or cleaned_query in product_name_lower:
            return product
    
    return None


def is_specific_product_query(message):
    """Check if user is asking about a specific product"""
    message_lower = message.lower()
    patterns = ['tell me about', 'what about', 'info on', 'details on', 'about', 'do you have']
    return any(p in message_lower for p in patterns)


def is_product_search(message):
    """Check if user is searching for a product"""
    message_lower = message.lower()
    patterns = ['looking for', 'search', 'find', 'show me']
    return any(p in message_lower for p in patterns)


def is_product_query(message):
    """Check if user is asking about products"""
    message_lower = message.lower()
    return any(p in message_lower for p in ['product', 'products', 'have', 'available', 'stock', 'show me', 'list'])


def is_purchase_query(message):
    """Check if user is asking about purchasing"""
    message_lower = message.lower()
    return any(p in message_lower for p in ['buy', 'purchase', 'order', 'checkout', 'payment', 'shipping', 'cart'])


def search_products(query, products):
    """Search for products matching the user's query"""
    if not products:
        return []
    
    query_lower = query.lower()
    matching_products = []
    
    # Direct product name matches
    for product in products:
        product_name_lower = product['name'].lower()
        if product_name_lower in query_lower or query_lower in product_name_lower:
            matching_products.append((100, product))
    
    if matching_products:
        matching_products.sort(reverse=True, key=lambda x: x[0])
        return [p for score, p in matching_products]
    
    # Fuzzy matching with search terms
    search_terms = extract_search_terms(query_lower)
    
    for product in products:
        score = 0
        product_name_lower = product['name'].lower()
        product_desc_lower = product['description'].lower()
        
        for term in search_terms:
            if term and len(term) > 1:
                if term in product_name_lower:
                    score += 10
                elif term in product_desc_lower:
                    score += 3
        
        if score > 0:
            matching_products.append((score, product))
    
    matching_products.sort(reverse=True, key=lambda x: x[0])
    return [p for score, p in matching_products[:10]]


def extract_search_terms(query):
    """Extract search terms from natural language queries"""
    phrases_to_remove = ['do you have', 'is there', 'looking for', 'searching for', 
                         'tell me about', 'show me', 'what about', 'how about']
    
    cleaned_query = query
    for phrase in phrases_to_remove:
        if cleaned_query.startswith(phrase):
            cleaned_query = cleaned_query[len(phrase):]
            break
    
    cleaned_query = re.sub(r'[^\w\s]', ' ', cleaned_query)
    cleaned_query = ' '.join(cleaned_query.split())
    
    common_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
    terms = [term.strip() for term in cleaned_query.split() if term.strip() and term.strip() not in common_words]
    
    return terms if terms else [cleaned_query]


def generate_detailed_product_response(products, original_query):
    """Generate detailed response for specific product searches"""
    if not products:
        return None
    
    if len(products) == 1:
        product = products[0]
        response = f"**{product['name']}**\n\n"
        response += f"**Price:** ${product['price']}\n"
        response += f"**Sold by:** {product['business']}\n"
        response += f"**Description:**\n{product['description']}\n\n"
        response += "Would you like to know more about this product?"
    else:
        response = f"**I found {len(products)} products:**\n\n"
        for idx, product in enumerate(products[:5], 1):
            response += f"**{idx}. {product['name']}**\n"
            response += f"   ${product['price']} | {product['business']}\n"
        if len(products) > 5:
            response += f"\n*...and {len(products) - 5} more.*\n"
        response += "\nWhich one would you like to know more about?"
    
    return response


def generate_product_listing_response(products):
    """Generate product listing response"""
    if not products:
        return "I'm sorry, but there are no products available right now."
    
    response = "**Here are all the products available:**\n\n"
    
    for idx, product in enumerate(products[:10], 1):
        response += f"**{idx}. {product['name']}**\n"
        response += f"   Price: ${product['price']}\n"
        response += f"   {product['description'][:80]}...\n\n"
    
    response += "✨ Ask me about a specific product to see more details!"
    return response


def handle_purchase_query(query, products, user):
    """Handle purchase-related queries"""
    query_lower = query.lower()
    
    for product in products:
        if product['name'].lower() in query_lower:
            return generate_purchase_specific_product_response(product, user)
    
    return generate_general_purchase_response(products, user)


def generate_purchase_specific_product_response(product, user):
    """Generate response for purchasing a specific product"""
    response = f"**Ready to buy {product['name']}?**\n\n"
    response += f"Price: ${product['price']}\n"
    response += f"Sold by: {product['business']}\n\n"
    response += "**To purchase:**\n"
    response += "1. Go to the product page\n"
    response += "2. Click 'Add to Cart'\n"
    response += "3. Complete checkout\n\n"
    
    if not user.is_authenticated:
        response += "Note: You'll need to log in to complete your purchase.\n"
    
    return response


def generate_general_purchase_response(products, user):
    """Generate general response about purchasing"""
    response = "**Ready to Make a Purchase?**\n\n"
    
    if products:
        response += f"We have **{len(products)} products** available!\n\n"
    
    response += "**To buy:**\n"
    response += "• Browse our catalog\n"
    response += "• Ask me about specific products\n"
    response += "• Click 'Add to Cart' on any product\n"
    
    return response


def format_products_for_prompt(products):
    """Format products for the system prompt"""
    if not products:
        return "No products are currently available."
    
    formatted = ""
    for idx, product in enumerate(products[:20], 1):
        formatted += f"{idx}. {product['name']}\n"
        formatted += f"   Price: ${product['price']}\n"
        formatted += f"   {product['description'][:80]}...\n\n"
    
    return formatted
