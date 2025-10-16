import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class DemoModeMiddleware(MiddlewareMixin):
    """
    演示环境中间件
    全局禁止修改和删除操作
    """

    def process_request(self, request):
        # 只处理 API 请求
        if not request.path.startswith('/api/'):
            return None

        # 禁止的 HTTP 方法
        forbidden_methods = ['POST', 'PUT', 'PATCH', 'DELETE']

        if request.method in forbidden_methods:
            # 检查是否是登录接口，登录接口允许 POST
            if request.path.endswith('/login/') or request.path.endswith('/auth/login/'):
                return None

            # 检查是否是登出接口，登出接口允许 POST
            if request.path.endswith('/logout/') or request.path.endswith('/auth/logout/'):
                return None

            # 其他修改/删除操作一律禁止
            response_data = {
                'code': 403,
                'message': '演示环境禁止修改和删除操作',
                'data': None
            }

            return JsonResponse(
                response_data,
                status=status.HTTP_403_FORBIDDEN,
                content_type='application/json'
            )

        return None