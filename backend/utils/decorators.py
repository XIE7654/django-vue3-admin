from rest_framework.response import Response
from rest_framework import status
from utils.idempotency_helper import generate_idempotency_key, check_idempotency, get_user_identifier


def idempotent(timeout=10):
    """
    幂等性装饰器，用于单个DRF接口
    :param timeout: 重复判断时间窗口（秒）
    """

    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            user_id = get_user_identifier(request)
            key = generate_idempotency_key(user_id, request.path, request.body)

            if check_idempotency(key, timeout):
                return Response(
                    {"error": "请勿重复提交"},
                    status=status.HTTP_409_CONFLICT
                )

            return view_func(self, request, *args, **kwargs)

        return wrapper

    return decorator
