from openai import OpenAI
from django.conf import settings


def get_ai_response(user_message, products, user):
    """
    Get AI response using OpenAI API with product context
    """
    if not settings.OPENAI_API_KEY:
        return "AI service is not configured. Please set OPENAI_API_KEY in settings."
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Build product context
    product_context = "Available products:\n"
    for product in products:
        product_context += f"- {product.name}: {product.description} (Price: ${product.price})\n"
    
    if not products:
        product_context = "No products are currently available."
    
    # System prompt
    system_prompt = f"""You are a helpful assistant for a product marketplace. 
You can answer questions about available products, help users find products, and provide information about pricing.

{product_context}

Answer user questions based on the available products. If a user asks about products that don't exist, 
politely inform them. Be concise and helpful."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"
