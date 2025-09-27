from system.models import Config
from utils.serializers import CustomModelSerializer
from utils.custom_model_viewSet import CustomModelViewSet
from django_filters import rest_framework as filters, CharFilter


class ConfigSerializer(CustomModelSerializer):
    """
    参数配置 序列化器
    """
    class Meta:
        model = Config
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']


class ConfigFilter(filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    key = CharFilter(field_name='key', lookup_expr='icontains')
    value = CharFilter(field_name='value', lookup_expr='icontains')
    remark = CharFilter(field_name='remark', lookup_expr='icontains')

    class Meta:
        model = Config
        fields = ['id', 'remark', 'creator', 'modifier', 'is_deleted', 'name', 'key', 'value', 'config_type']


class ConfigViewSet(CustomModelViewSet):
    """
    参数配置 视图集
    """
    queryset = Config.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ConfigSerializer
    filterset_class = ConfigFilter
    search_fields = ['name']  # 根据实际字段调整
    ordering_fields = ['create_time', 'id']
    ordering = ['-create_time']
