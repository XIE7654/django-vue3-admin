"""
@Remark: 自定义序列化器
"""
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from django.utils.functional import cached_property
from rest_framework.utils.serializer_helpers import BindingDict


class AuditUserFieldsMixin:
    """
    用于自动赋值 creator 和 modifier 字段的 Mixin
    """
    # 修改人的审计字段名称, 默认modifier, 继承使用时可自定义覆盖
    modifier_field_id = 'modifier'
    # 创建人的审计字段名称, 默认creator, 继承使用时可自定义覆盖
    creator_field_id = 'creator'

    def set_audit_user_fields(self, validated_data, is_create=True):
        username = self.get_request_username() if hasattr(self, 'get_request_username') else None
        if getattr(self, 'request', None):
            if self.modifier_field_id in self.fields:
                validated_data[self.modifier_field_id] = username
            if is_create and self.creator_field_id in self.fields:
                validated_data[self.creator_field_id] = username


class CustomModelSerializer(AuditUserFieldsMixin, ModelSerializer):
    """
    增强DRF的ModelSerializer,可自动更新模型的审计字段记录
    (1)self.request能获取到rest_framework.request.Request对象
    """
    # 添加默认时间返回格式
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    def __init__(self, instance=None, data=empty, request=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.request: Request = request or self.context.get('request', None)

    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        self.set_audit_user_fields(validated_data, is_create=True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.set_audit_user_fields(validated_data, is_create=False)
        return super().update(instance, validated_data)

    def get_request_username(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'username', None)
        return None

    def get_request_name(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'name', None)
        return None

    def get_request_user_id(self):
        if getattr(self.request, 'user', None):
            return getattr(self.request.user, 'id', None)
        return None

    @cached_property
    def fields(self):
        fields = BindingDict(self)
        for key, value in self.get_fields().items():
            fields[key] = value

        if not hasattr(self, '_context'):
            return fields
        is_root = self.root == self
        parent_is_list_root = self.parent == self.root and getattr(self.parent, 'many', False)
        if not (is_root or parent_is_list_root):
            return fields

        try:
            request = self.request or self.context['request']
        except KeyError:
            return fields
        params = getattr(
            request, 'query_params', getattr(request, 'GET', None)
        )
        if params is None:
            pass
        try:
            filter_fields = params.get('_fields', None).split(',')
        except AttributeError:
            filter_fields = None

        try:
            omit_fields = params.get('_exclude', None).split(',')
        except AttributeError:
            omit_fields = []

        existing = set(fields.keys())
        if filter_fields is None:
            allowed = existing
        else:
            allowed = set(filter(None, filter_fields))

        omitted = set(filter(None, omit_fields))
        for field in existing:
            if field not in allowed:
                fields.pop(field, None)
            if field in omitted:
                fields.pop(field, None)

        return fields
