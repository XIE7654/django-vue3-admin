import asyncio

from django.http import StreamingHttpResponse
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ai.llm.enums import LLMProvider
from ai.llm.factory import get_adapter
from ai.models import ChatMessage
from backend import settings
from models.ai import MessageType
from utils.serializers import CustomModelSerializer
from utils.custom_model_viewSet import CustomModelViewSet
from django_filters import rest_framework as filters


class ChatMessageSerializer(CustomModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    """
    AI 聊天消息 序列化器
    """
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']


class ChatMessageFilter(filters.FilterSet):

    class Meta:
        model = ChatMessage
        fields = ['id', 'remark', 'creator', 'modifier', 'is_deleted', 'conversation_id',
                  'model', 'type', 'reply_id', 'content', 'use_context', 'segment_ids']


class ChatMessageViewSet(CustomModelViewSet):
    """
    AI 聊天消息 视图集
    """
    queryset = ChatMessage.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ChatMessageSerializer
    filterset_class = ChatMessageFilter
    search_fields = ['name']  # 根据实际字段调整
    ordering_fields = ['create_time', 'id']
    ordering = ['-create_time']

    @action(detail=False, methods=['post'], url_path='stream')
    def stream(self, request):
        """
        流式聊天接口
        """
        content = request.data.get('content')
        conversation_id = request.data.get('conversation_id')
        platform = request.data.get('platform', 'deepseek')

        # 获取平台配置
        if platform == 'tongyi':
            model = 'qwen-plus'
            api_key = settings.DASHSCOPE_API_KEY
            provider = LLMProvider.TONGYI
        else:
            # 默认使用 DeepSeek
            model = 'deepseek-chat'
            api_key = settings.DEEPSEEK_API_KEY
            provider = LLMProvider.DEEPSEEK

        # 获取当前用户
        user_id = request.user.id

        try:
            # 获取或创建对话
            conversation = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('id')
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 添加用户消息
        ChatMessage.objects.create(
            conversation_id=conversation_id,
            user_id=user_id,
            role_id=None,
            model=model,
            model_id=None,
            type=MessageType.USER,
            reply_id=None,
            content=content,
            use_context=True,
            segment_ids=None,
        )
        # 构建上下文
        context = [("system", "You are a helpful assistant")]
        history = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('id')

        for msg in history:
            context.append((msg.type, msg.content))

        # 获取LLM适配器
        llm = get_adapter(provider, api_key=api_key, model=model)

        # 创建流式响应

        # 8. 同步生成器（包装异步LLM流，核心修复点）
        def generate():
            ai_reply = ""
            loop = None
            try:
                # 创建新的事件循环（避免复用主线程循环）
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # 异步生成器包装函数
                async def async_stream():
                    # 调用LLM的异步流式接口（假设 llm.stream_chat 是 async_generator）
                    async for chunk in llm.stream_chat(context):
                        yield chunk

                # 将异步生成器转换为同步迭代
                async_gen = async_stream()
                while True:
                    try:
                        # 逐个获取异步chunk
                        chunk = loop.run_until_complete(async_gen.__anext__())
                    except StopAsyncIteration:
                        break  # 流结束，退出循环
                    except Exception as e:
                        # 捕获LLM流异常，返回错误信息
                        yield f"data: 错误：{str(e)}\n\n"
                        break

                    # 提取chunk内容（适配不同LLM的返回格式）
                    if hasattr(chunk, 'content'):
                        chunk_content = chunk.content.strip()
                    elif isinstance(chunk, dict) and 'content' in chunk:
                        chunk_content = chunk['content'].strip()
                    else:
                        chunk_content = str(chunk).strip()

                    # 只返回非空内容
                    if chunk_content:
                        ai_reply += chunk_content
                        # 遵循SSE格式：data: 内容\n\n（必须以\n\n结尾）
                        yield f"data: {chunk_content}\n\n"

            finally:
                # 关闭事件循环（避免资源泄漏）
                if loop:
                    loop.close()
            # 保存AI回复
            if ai_reply.strip():
                ChatMessage.objects.create(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role_id=None,
                    model=model,
                    model_id=None,
                    type=MessageType.ASSISTANT,
                    reply_id=None,
                    content=ai_reply,
                    use_context=True,
                    segment_ids=None,
                )

        return StreamingHttpResponse(generate(), content_type='text/event-stream')
