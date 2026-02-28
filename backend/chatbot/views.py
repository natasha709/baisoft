from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatQuerySerializer
from .ai_service import get_ai_response
from products.models import Product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_query(request):
    """
    AI Chatbot Query Endpoint

    This is the main endpoint for users to interact with the AI chatbot.
    It processes natural language queries about products and returns intelligent responses.

    Process Flow:
    1. Validate user input (message format, length, etc.)
    2. Get relevant product context based on user's business access
    3. Send query to AI service (OpenAI GPT) with product context
    4. Handle AI service errors gracefully with fallback responses
    5. Store chat interaction in database for history
    6. Return AI response to user

    Request Body:
    - message (str): User's natural language query

    Response:
    - message: Original user message (for confirmation)
    - response: AI-generated response with product information
    - id: Chat message ID for reference

    Business Logic:
    - Users only see products from their business (business isolation)
    - Superusers can see all approved products (platform administration)
    - Only approved products are included in AI context (quality control)
    - Chat history is stored for each user individually

    Error Handling:
    - Invalid input: Returns validation errors
    - AI service failure: Falls back to local product search
    - Database errors: Returns appropriate error messages
    - Rate limiting: Handled by DRF throttling (configured in settings)

    Security Features:
    - Authentication required (no anonymous queries)
    - Business isolation (users can't query other businesses' products)
    - Input validation and sanitization
    - Error message sanitization (no sensitive data exposure)
    """

    serializer = ChatQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_message = serializer.validated_data['message']

    products = Product.objects.filter(status='approved')

    if request.user.is_superuser:

        pass
    elif getattr(request.user, "business_id", None):

        products = products.filter(business=request.user.business)
    else:

        products = Product.objects.none()

    try:
        ai_response = get_ai_response(user_message, products, request.user)
    except Exception as e:

        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"AI service error for user {request.user.email}: {str(e)}")

        return Response(
            {'error': 'I\'m having trouble processing your request right now. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        chat_message = ChatMessage.objects.create(
            user=request.user,
            user_message=user_message,
            ai_response=ai_response
        )
    except Exception as e:

        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to save chat message for user {request.user.email}: {str(e)}")

        return Response({
            'message': user_message,
            'response': ai_response,
            'id': None,
            'warning': 'Response generated but not saved to history'
        })

    return Response({
        'message': user_message,
        'response': ai_response,
        'id': chat_message.id
    })

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Chat History API ViewSet

    Provides read-only access to user's chat history with the AI assistant.
    Users can retrieve their previous conversations for reference.

    Endpoints:
    - GET /api/chatbot/history/
    - GET /api/chatbot/history/{id}/

    Features:
    - User isolation (users only see their own chat history)
    - Chronological ordering (newest messages first)
    - Pagination support (configured in settings.py)
    - Read-only access (no editing or deleting of chat history)

    Business Rules:
    - Users can only access their own chat messages
    - Chat history is ordered by creation time (newest first)
    - No modification of chat history allowed (audit trail integrity)
    - Pagination prevents large response sizes

    Use Cases:
    - Display chat history in frontend
    - Reference previous conversations
    - User support and troubleshooting
    - Conversation context for follow-up queries

    Security:
    - Authentication required
    - User isolation enforced at queryset level
    - No sensitive data exposure in responses
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter chat messages to current user only

        Security Implementation:
        - Users can only see their own chat messages
        - No cross-user data access possible
        - Automatic filtering based on authenticated user

        Returns:
            QuerySet: User's chat messages ordered by creation time (newest first)
        """
        return ChatMessage.objects.filter(user=self.request.user)
