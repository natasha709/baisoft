from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'history', views.ChatMessageViewSet, basename='chat-history')

urlpatterns = [
    path('query/', views.chat_query, name='chat-query'),
    path('', include(router.urls)),
]
