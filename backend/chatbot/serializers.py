from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user_message', 'ai_response', 'created_at']
        read_only_fields = ['id', 'ai_response', 'created_at']

class ChatQuerySerializer(serializers.Serializer):
    message = serializers.CharField()
