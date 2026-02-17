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
    serializer = ChatQuerySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    
    # Get approved products for context
    products = Product.objects.filter(status='approved')
    
    # Get AI response
    try:
        ai_response = get_ai_response(user_message, products, request.user)
    except Exception as e:
        return Response(
            {'error': f'AI service error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Save chat message
    chat_message = ChatMessage.objects.create(
        user=request.user,
        user_message=user_message,
        ai_response=ai_response
    )
    
    return Response({
        'message': user_message,
        'response': ai_response,
        'id': chat_message.id
    })


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)
