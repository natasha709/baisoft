from openai import OpenAI
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

def get_ai_response(user_message, products, user):
    """
    Get AI response using OpenAI API with product context
    """
    try:
        if not settings.OPENAI_API_KEY:
            # If no API key, use local product search only
            return handle_local_product_query(user_message, products, user)
        
        # Initialize OpenAI client with minimal configuration
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )
        model = getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Build product context with detailed information
        product_list = []
        if products:
            for product in products:
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': str(product.price),
                    'business': product.business.name,
                })
        
        # Try to use OpenAI, but fall back to local search if it fails
        try:
            # Handle purchase-related queries
            if is_purchase_query(user_message):
                return handle_purchase_query(user_message, product_list, user)
            
            # Check if this is a product search query
            if is_product_search(user_message) or is_specific_product_query(user_message):
                matching_products = search_products(user_message, product_list)
                if matching_products:
                    return generate_detailed_product_response(matching_products, user_message)
                else:
                    # No matches found, but still show all products
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
            logger.error(f"OpenAI API error: {str(e)}")
            # Fall back to local product handling
            return handle_local_product_query(user_message, products, user)
        
    except Exception as e:
        logger.error(f"AI service error: {str(e)}")
        return handle_local_product_query(user_message, products, user)

def handle_local_product_query(user_message, products, user):
    """
    Handle product queries locally without using OpenAI
    """
    # Convert products to list of dicts for consistent handling
    product_list = []
    if products:
        for product in products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'business': product.business.name
            })
    
    # First, try to find if this is a direct product mention (even without spaces)
    direct_product_match = find_direct_product_match(user_message, product_list)
    if direct_product_match:
        return generate_detailed_product_response([direct_product_match], user_message)
    
    # Check for specific product queries
    if is_specific_product_query(user_message) or is_product_search(user_message):
        matching_products = search_products(user_message, product_list)
        if matching_products:
            return generate_detailed_product_response(matching_products, user_message)
        else:
            # No matches found
            search_term = extract_search_terms(user_message)[0] if extract_search_terms(user_message) else "that"
            return f"🔍 I couldn't find any products matching '{search_term}'.\n\n{generate_product_listing_response(product_list)}"
    
    # Check for purchase queries
    if is_purchase_query(user_message):
        return handle_purchase_query(user_message, product_list, user)
    
    # Default to product listing
    return generate_product_listing_response(product_list)

def find_direct_product_match(query, products):
    """
    Find if the query directly mentions a product name (even without spaces)
    """
    if not products:
        return None
    
    query_lower = query.lower()
    
    # Remove common prefixes to get to the potential product name
    prefixes = [
        'tell me about', 'tell me aboutthe', 'tell me abouta', 'tell me aboutan',
        'what about', 'how about', 'info on', 'details on', 'about',
        'tell me about', 'tell me about ', 'about ', 'aboutthe', 'abouta', 'aboutan'
    ]
    
    cleaned_query = query_lower
    for prefix in prefixes:
        if cleaned_query.startswith(prefix):
            cleaned_query = cleaned_query[len(prefix):]
            break
    
    # Remove any remaining common words
    common_words = ['the', 'a', 'an', 'is', 'are', 'was', 'were']
    for word in common_words:
        if cleaned_query.startswith(word + ' '):
            cleaned_query = cleaned_query[len(word)+1:]
        elif cleaned_query.endswith(' ' + word):
            cleaned_query = cleaned_query[:-(len(word)+1)]
    
    cleaned_query = cleaned_query.strip()
    
    # Check if cleaned query matches any product name exactly or partially
    for product in products:
        product_name_lower = product['name'].lower()
        
        # Exact match
        if cleaned_query == product_name_lower:
            return product
        
        # Product name contains the cleaned query
        if cleaned_query in product_name_lower:
            return product
        
        # Cleaned query contains product name
        if product_name_lower in cleaned_query:
            return product
    
    return None

def is_specific_product_query(message):
    """
    Check if the user is asking about a specific product
    """
    message_lower = message.lower()
    
    # Patterns that indicate asking about a specific product
    specific_patterns = [
        r'^(?:tell me about|what about|how about|info(?:rmation)? on|details? on|about)\s*(.+?)$',
        r'^(?:do you have|is there)\s*(?:a|an)?\s*(.+?)(?:\?|$)',
        r'^(?:i want|i need|i\'m looking for)\s*(?:the|a|an)?\s*(.+?)$',
        r'^(.+?)\s+(?:info|information|details)$',
        r'^(?:show|display|get)\s+(?:me\s+)?(?:info|information|details)?\s*(?:on|about)?\s*(.+?)$',
    ]
    
    for pattern in specific_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    
    return False

def is_product_search(message):
    """
    Check if the user is searching for a specific product
    """
    message_lower = message.lower()
    
    search_patterns = [
        r'(?:do you have|is there|looking for|search(?:ing)? for|find)\s*(.+?)(?:\?|$)',
        r'(?:what about|how about|tell me more about)\s*(?:the\s+)?(.+?)(?:\?|$)',
        r'(?:i want|i need|i\'m looking for)\s*(?:a|an|the)?\s*(.+?)(?:\?|$)',
        r'^(.+?)(?:\?)?$',  # Any single phrase could be a product search
    ]
    
    for pattern in search_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    
    return False

def search_products(query, products):
    """
    Search for products matching the user's query
    """
    if not products:
        return []
    
    query_lower = query.lower()
    matching_products = []
    
    # First, try to find direct product name matches (highest priority)
    for product in products:
        product_name_lower = product['name'].lower()
        
        # Check if product name appears in query (even without spaces)
        if product_name_lower in query_lower or query_lower in product_name_lower:
            # Calculate a high score for direct matches
            score = 100
            matching_products.append((score, product))
            continue
    
    if matching_products:
        # Sort by score and return
        matching_products.sort(reverse=True, key=lambda x: x[0])
        return [p for score, p in matching_products]
    
    # If no direct matches, try fuzzy matching with search terms
    search_terms = extract_search_terms(query_lower)
    
    for product in products:
        score = 0
        product_name_lower = product['name'].lower()
        product_desc_lower = product['description'].lower()
        
        if search_terms:
            for term in search_terms:
                if term and len(term) > 1:
                    # Name contains term
                    if term in product_name_lower:
                        score += 10
                    # Description contains term
                    elif term in product_desc_lower:
                        score += 3
        else:
            # If no specific terms extracted, check if query is in name or description
            if query_lower in product_name_lower:
                score += 5
            elif query_lower in product_desc_lower:
                score += 2
        
        # Check for word matches
        query_words = set(query_lower.split())
        product_words = set(product_name_lower.split())
        common_words = query_words.intersection(product_words)
        score += len(common_words) * 5
        
        if score > 0:
            matching_products.append((score, product))
    
    # Sort by relevance score
    matching_products.sort(reverse=True, key=lambda x: x[0])
    return [p for score, p in matching_products]

def extract_search_terms(query):
    """
    Extract search terms from natural language queries, handling cases without spaces
    """
    # Remove common question phrases
    phrases_to_remove = [
        'do you have', 'is there', 'looking for', 'searching for',
        'tell me about', 'information about', 'details about', 'show me',
        'what about', 'how about', 'tell me more about', 'i want',
        'i need', 'i\'m looking for', 'can you show', 'can you tell',
        'find', 'search', 'info on', 'details on', 'about', 'tell me about',
        'tell me aboutthe', 'tell me abouta', 'tell me aboutan',
        'aboutthe', 'abouta', 'aboutan'
    ]
    
    cleaned_query = query
    for phrase in phrases_to_remove:
        if cleaned_query.startswith(phrase):
            cleaned_query = cleaned_query[len(phrase):]
            break
    
    # Remove question marks, punctuation, and extra spaces
    cleaned_query = re.sub(r'[^\w\s]', ' ', cleaned_query)
    cleaned_query = ' '.join(cleaned_query.split())
    
    # Split into terms and filter out common words
    common_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'is', 'are'}
    terms = [term.strip() for term in cleaned_query.split() if term.strip() and term.strip() not in common_words]
    
    return terms if terms else [cleaned_query]

def generate_detailed_product_response(products, original_query):
    """
    Generate a detailed response for specific product searches
    """
    if not products:
        return None
    
    if len(products) == 1:
        # Single product match - show detailed view
        product = products[0]
        response = f"**✨ {product['name']}**\n\n"
        response += f"**💰 Price:** ${product['price']}\n"
        response += f"**🏪 Sold by:** {product['business']}\n"
        response += f"**📝 Description:**\n{product['description']}\n\n"
        response += "💡 **Would you like to know more about this product or perhaps buy it?**"
        
    else:
        # Multiple matches found - show summary
        response = f"🔍 **I found {len(products)} products matching your search:**\n\n"
        
        for idx, product in enumerate(products[:5], 1):
            response += f"**{idx}. {product['name']}**\n"
            response += f"   💰 ${product['price']} | 🏪 {product['business']}\n"
            response += f"   📝 {product['description'][:100]}...\n\n"
        
        if len(products) > 5:
            response += f"*...and {len(products) - 5} more matches.*\n\n"
        
        response += "**Which one would you like to know more about?**"
    
    return response

def is_product_query(message):
    """
    Check if the user is asking about products
    """
    message_lower = message.lower()
    
    product_phrases = [
        'product', 'products', 'have', 'available', 'stock', 'items', 
        'catalog', 'listing', 'what do you', 'show me', 'list',
        'all products', 'what products'
    ]
    
    for phrase in product_phrases:
        if phrase in message_lower:
            return True
    
    return False

def is_purchase_query(message):
    """
    Check if the user is asking about purchasing
    """
    message_lower = message.lower()
    
    purchase_keywords = [
        'buy', 'purchase', 'order', 'checkout', 'payment', 
        'shipping', 'delivery', 'cart'
    ]
    
    for keyword in purchase_keywords:
        if keyword in message_lower:
            return True
    
    return False

def format_products_for_prompt(products):
    """
    Format products for the system prompt
    """
    if not products:
        return "No products are currently available in the marketplace."
    
    formatted = ""
    for idx, product in enumerate(products, 1):
        formatted += f"{idx}. {product['name']}\n"
        formatted += f"   Price: ${product['price']}\n"
        formatted += f"   Description: {product['description'][:100]}...\n"
        formatted += f"   Sold by: {product['business']}\n\n"
    
    return formatted

def generate_product_listing_response(products):
    """
    Generate a formatted response for product listing queries
    """
    if not products:
        return " I'm sorry, but there are currently no products available in the marketplace. Please check back later!"
    
    response = " **Here are all the products available in our marketplace:**\n\n"
    
    for idx, product in enumerate(products, 1):
        response += f"**{idx}. {product['name']}**\n"
        response += f" Price: ${product['price']}\n"
        response += f" Description: {product['description'][:150]}...\n"
        response += f" Sold by: {product['business']}\n\n"
    
    response += "✨ **To see details about a specific product, just ask!** (e.g., 'Tell me about maize' or 'Show me beans')"
    return response

def handle_purchase_query(query, products, user):
    """
    Handle purchase-related queries
    """
    query_lower = query.lower()
    
    # Check if they're asking about a specific product
    for product in products:
        if product['name'].lower() in query_lower:
            return generate_purchase_specific_product_response(product, user)
    
    # General purchase response
    return generate_general_purchase_response(products, user)

def generate_purchase_specific_product_response(product, user):
    """
    Generate response for purchasing a specific product
    """
    response = f"** Ready to buy {product['name']}?**\n\n"
    
    response += f"**Product Details:**\n"
    response += f" Price: ${product['price']}\n"
    response += f" Sold by: {product['business']}\n\n"
    
    response += "**To purchase this product:**\n"
    response += "1. Go to the product page\n"
    response += "2. Click 'Add to Cart' or 'Buy Now'\n"
    response += "3. Follow the checkout process\n\n"
    
    if not user.is_authenticated:
        response += " **Note:** You'll need to log in to complete your purchase.\n"
    
    return response

def generate_general_purchase_response(products, user):
    """
    Generate general response about purchasing
    """
    response = "** Ready to Make a Purchase?**\n\n"
    
    if products:
        response += f"We have **{len(products)} products** available!\n\n"
        
        # Show a few products
        response += "**Popular items:**\n"
        for product in list(products)[:3]:
            response += f"• {product['name']} - ${product['price']}\n"
        
        response += "\n"
    
    response += "**To buy a product:**\n"
    response += "• Browse our catalog\n"
    response += "• Ask me about specific products\n"
    response += "• Click 'Add to Cart' on any product\n"
    
    return response