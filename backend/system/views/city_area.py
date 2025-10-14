from system.models import CityArea
from utils.serializers import CustomModelSerializer
from utils.custom_model_viewSet import CustomModelViewSet
from django_filters import rest_framework as filters


class CityAreaSerializer(CustomModelSerializer):
    """
    省市区 序列化器
    """
    class Meta:
        model = CityArea
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']


class CityAreaFilter(filters.FilterSet):

    class Meta:
        model = CityArea
        fields = ['id', 'remark', 'creator', 'modifier', 'is_deleted', 'prov_id', 'prov_name', 'city_id', 'city_name', 'area_id', 'area_name']


class CityAreaViewSet(CustomModelViewSet):
    """
    省市区 视图集
    """
    queryset = CityArea.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = CityAreaSerializer
    filterset_class = CityAreaFilter
    search_fields = ['name']  # 根据实际字段调整
    ordering_fields = ['create_time', 'id']
    ordering = ['-create_time']
