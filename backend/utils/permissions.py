from rest_framework import permissions
from rest_framework.permissions import BasePermission
from system.models import Menu
from utils.string_utils import camel_to_snake


class IsSuperUserOrReadOnly(BasePermission):
    """超级用户可读写，普通用户只读"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser



class HasButtonPermission(BasePermission):
    """
    通用按钮权限校验
    用法：在视图中设置 required_permission = 'xxx:xxx:xxx'
    """
    def has_permission(self, request, view):
        required_code = getattr(view, 'required_permission', None)
        if not required_code:
            # 可自动推断权限编码逻辑
            app_label = view.queryset.model._meta.app_label
            model_name = camel_to_snake(view.queryset.model._meta.model_name)
            action = getattr(view, 'action', None)
            action_map = {
                'create': 'create',
                'update': 'edit',
                'partial_update': 'edit',
                'destroy': 'delete',
                'list': 'query',
                'retrieve': 'query',
            }
            if action in action_map:
                required_code = f"{app_label}:{model_name}:{action_map[action]}"
        if not required_code:
            return True  # 不需要按钮权限
        user = request.user
        if not user.is_authenticated or user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        role_ids = user.role.values_list('id', flat=True)
        return Menu.objects.filter(
            type='button',
            role__id__in=role_ids,
            auth_code=required_code
        ).exists()
