from rest_framework import viewsets, status
from rest_framework.response import Response

from utils.export_mixin import ExportMixin


class CustomModelViewSet(viewsets.ModelViewSet, ExportMixin):
    """
    自定义ModelViewSet，提供以下增强功能：
    - 基于动作的序列化器选择
    - 基于动作的权限控制
    - 标准化响应格式
    - 软删除支持
    - 批量操作支持
    """
    # 动作到序列化器类的映射
    action_serializers = {}
    # 动作到权限类的映射
    action_permissions = {}
    # 软删除字段名
    soft_delete_field = 'is_deleted'
    # 是否支持软删除
    enable_soft_delete = False

    def get_required_permission(self):
        # 约定：system:menu:create
        app_label = self.queryset.model._meta.app_label
        model_name = self.queryset.model._meta.model_name
        action = self.action  # 'create', 'update', 'destroy', 'list', 'retrieve'
        # 只对增删改查等操作做权限控制
        action_map = {
            'create': 'create',
            'update': 'edit',
            'partial_update': 'edit',
            'destroy': 'delete',
            'list': 'query',
            'retrieve': 'query',
        }
        if action in action_map:
            perm_action = action_map[action]
        else:
            perm_action = action  # 如 sync、import、export
        return f"{app_label}:{model_name}:{perm_action}"

    def get_permissions(self):
        permissions = super().get_permissions()
        required_code = self.get_required_permission()
        if required_code:
            from utils.permissions import HasButtonPermission
            perm = HasButtonPermission()
            # 动态设置 required_permission
            perm.required_permission = required_code
            permissions.append(perm)
        return permissions


    def get_serializer_class(self):
        """根据当前动作获取序列化器类"""
        return self.action_serializers.get(
            self.action,
            super().get_serializer_class()
        )


    def list(self, request, *args, **kwargs):
        """重写列表视图，支持软删除过滤"""
        queryset = self.get_queryset()
        # 应用软删除过滤
        if self.enable_soft_delete:
            queryset = queryset.filter(**{self.soft_delete_field: False})
        # 应用搜索和过滤
        queryset = self.filter_queryset(queryset)

        # 判断是否传了 page 参数
        if 'page' in request.query_params:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        # 没有 page 参数，返回全部数据
        serializer = self.get_serializer(queryset, many=True)
        return self._build_response(
            data=serializer.data,
            message="ok",
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """重写详情视图，支持软删除检查"""
        instance = self.get_object()

        # 检查软删除状态
        if (self.enable_soft_delete and
                hasattr(instance, self.soft_delete_field) and
                getattr(instance, self.soft_delete_field)):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return self._build_response(
            data=serializer.data,
            message="Object retrieved successfully",
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        """重写创建视图，支持批量创建"""
        is_many = isinstance(request.data, list)

        if is_many:
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return self._build_response(
            data=serializer.data,
            message="ok",
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self._build_response(
            message="ok",
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return self._build_response(
            data=serializer.data,
            message="ok",
            status=status.HTTP_200_OK,
        )

    def _build_response(self, code=0, message="成功", data=None, status=status.HTTP_200_OK):
        """
        构建标准化API响应格式

        参数说明:
        - code: 业务状态码（0表示成功，非0表示错误）
        - message: 状态描述信息
        - data: 响应数据（可为None）
        - status: HTTP状态码（默认200）
        """
        # 构建基础响应结构
        response_data = {
            "code": code,
            "message": message
        }

        # 仅当data不为None时添加到响应中
        if data is not None:
            response_data["data"] = data

        # 移除可能的空值（如message为空字符串）
        response_data = {k: v for k, v in response_data.items() if v is not None and v != ""}

        # 返回DRF的Response对象
        return Response(
            data=response_data,
            status=status,
            content_type="application/json"
        )
