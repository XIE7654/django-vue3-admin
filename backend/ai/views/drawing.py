import os
from datetime import datetime

from rest_framework.response import Response

from ai.models import Drawing
from backend import settings
from llm.enums import LLMProvider
from llm.factory import get_adapter
from utils.serializers import CustomModelSerializer
from utils.custom_model_viewSet import CustomModelViewSet
from django_filters import rest_framework as filters


class DrawingSerializer(CustomModelSerializer):
    """
    AI 绘画表 序列化器
    """
    class Meta:
        model = Drawing
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']


class DrawingFilter(filters.FilterSet):

    class Meta:
        model = Drawing
        fields = ['id', 'remark', 'creator', 'modifier', 'is_deleted', 'public_status', 'platform',
                  'model', 'width', 'height', 'status', 'pic_url', 'error_message', 'task_id', 'buttons']


class DrawingViewSet(CustomModelViewSet):
    """
    AI 绘画表 视图集
    """
    queryset = Drawing.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = DrawingSerializer
    filterset_class = DrawingFilter
    search_fields = ['name']  # 根据实际字段调整
    ordering_fields = ['create_time', 'id']
    ordering = ['-create_time']

    def create(self, request, *args, **kwargs):
        model = request.data.get('model')
        prompt = request.data.get('prompt')
        n = request.data.get('n', 1)
        style = request.data.get('style')
        size = request.data.get('size')
        api_key = settings.DASHSCOPE_API_KEY
        request.data['width'] = int(size.split('*')[0])
        request.data['height'] = int(size.split('*')[1])
        adapter = get_adapter(LLMProvider.TONGYI, api_key=api_key, model=model)
        rsp = adapter.create_drawing_task(prompt=prompt, n=n, style=style, size=size)
        if rsp['status_code'] != 200:
            return Response(rsp['data'], status=rsp['status_code'])
        else:
            request.data['status'] = rsp['output']['task_status']
            request.data['task_id'] = rsp['output']['task_id']
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in ("PENDING", 'RUNNING'):
            api_key = settings.DASHSCOPE_API_KEY
            adapter = get_adapter(LLMProvider.TONGYI, api_key=api_key, model='')
            rsp = adapter.fetch_drawing_task_status(instance.task_id)
            print(rsp, 'sadsadas')
            if rsp['status_code'] == 200:
                # 可根据 status.output.task_status 更新数据库
                if rsp['output']['task_status'] == 'SUCCEEDED':
                    instance.update_time = datetime.now()
                    instance.status = rsp['output']['task_status']
                    instance.pic_url = rsp['output']['results'][0]['url']
                elif rsp['output']['task_status'] == 'FAILED':
                    instance.update_time = datetime.now()
                    instance.status = rsp['output']['task_status']
                    instance.error_message = rsp['output']['message']
                elif rsp['output']['task_status'] == 'RUNNING':
                    instance.update_time = datetime.now()
                    instance.status = rsp['output']['task_status']
                instance.save()
        return super().retrieve(request, *args, **kwargs)
