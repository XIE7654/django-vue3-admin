from rest_framework import serializers, viewsets
from system.models import DictData
from utils.custom_model_viewSet import CustomModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from utils.models import CommonStatus


class DictDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = DictData
        fields = '__all__'


class DictDataFilter(filters.FilterSet):
    class Meta:
        model = DictData
        fields = ['dict_type']


class DictDataLabelValueSerializer(serializers.ModelSerializer):
    dict_type = serializers.CharField(source='dict_type.value')

    class Meta:
        model = DictData
        fields = ['label', 'value', 'dict_type']


class DictDataViewSet(CustomModelViewSet):
    queryset = (DictData.objects.filter(is_deleted=False).select_related('dict_type')
                .order_by('dict_type__id', 'sort'))
    serializer_class = DictDataSerializer
    filterset_class = DictDataFilter

    @action(detail=False, methods=['get'])
    def simple(self, request):
        # 复用filterset_class过滤DictData
        queryset = self.get_queryset().filter(status=CommonStatus.ENABLED)
        serializer = DictDataLabelValueSerializer(queryset, many=True)
        return self._build_response(data=serializer.data)