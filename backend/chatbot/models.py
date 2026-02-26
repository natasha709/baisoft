# Chatbot Data Models
# This module defines the database models for the AI chatbot system.
# It stores chat history and provides audit trail for AI interactions.
#
# Key Features:
# - Chat message storage with user association
# - Conversation history tracking
# - Audit trail for AI responses
# - User-specific chat isolation
# - Chronological message ordering

from django.db import models
from businesses.models import User


class ChatMessage(models.Model):
    """
    Chat Message Model for AI Chatbot System
    
    Stores individual chat interactions between users and the AI assistant.
    Each message contains both the user's question and the AI's response,
    creating a complete conversation record.
    
    Purpose:
    - Store chat history for user reference
    - Provide audit trail of AI interactions
    - Enable conversation context in future interactions
    - Support user-specific chat isolation
    - Track AI response quality and patterns
    
    Business Rules:
    - Each message belongs to a specific user (business isolation)
    - Messages are ordered chronologically (newest first)
    - Both user input and AI response are stored together
    - Deletion cascades when user is deleted (data cleanup)
    
    Use Cases:
    - Chat history display in frontend
    - Conversation context for AI responses
    - User behavior analysis
    - AI response quality monitoring
    - Audit trail for compliance
    """
    
    # User relationship - ensures chat isolation by business
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Delete messages when user is deleted
        related_name='chat_messages'  # Access user's messages via user.chat_messages
    )
    
    # Chat content - stores the complete conversation exchange
    user_message = models.TextField()  # User's question or input
    ai_response = models.TextField()   # AI assistant's response
    
    # Timestamp for conversation tracking
    created_at = models.DateTimeField(auto_now_add=True)  # When the chat occurred

    class Meta:
        # Order messages by newest first for chat history display
        ordering = ['-created_at']
        
        # Database indexes for performance
        indexes = [
            models.Index(fields=['user', '-created_at']),  # User's chat history queries
            models.Index(fields=['-created_at']),          # Recent messages queries
        ]

    def __str__(self):
        """
        String representation for admin interface and debugging
        
        Format: "user@email.com - YYYY-MM-DD HH:MM:SS"
        Helps identify messages in Django admin and logs
        """
        return f"{self.user.email} - {self.created_at}"

    def get_preview(self, length=50):
        """
        Get a preview of the user message for display purposes
        
        Args:
            length (int): Maximum length of preview text
            
        Returns:
            str: Truncated user message with ellipsis if needed
            
        Use Cases:
        - Chat history summaries
        - Admin interface previews
        - Notification text
        """
        if len(self.user_message) <= length:
            return self.user_message
        return self.user_message[:length] + "..."
