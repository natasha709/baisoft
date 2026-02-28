from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_message_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user_message', 'ai_response']
    readonly_fields = ['created_at']

    def user_message_preview(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = 'Message'
