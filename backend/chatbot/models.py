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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )

    user_message = models.TextField()
    ai_response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
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
