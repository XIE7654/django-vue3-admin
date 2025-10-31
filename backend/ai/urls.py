from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'api_key', views.AIApiKeyViewSet)
router.register(r'ai_model', views.AIModelViewSet)
router.register(r'tool', views.ToolViewSet)
router.register(r'knowledge', views.KnowledgeViewSet)
router.register(r'chat_conversation', views.ChatConversationViewSet)
router.register(r'chat_message', views.ChatMessageViewSet)
router.register(r'drawing', views.DrawingViewSet)


urlpatterns = [
    path('', include(router.urls)),
]