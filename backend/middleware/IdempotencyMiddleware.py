from django.http import JsonResponse
from utils.idempotency_helper import generate_idempotency_key, check_idempotency, get_user_identifier


class IdempotencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            user_id = get_user_identifier(request)
            key = generate_idempotency_key(user_id, request.path, request.body)

            if check_idempotency(key, 10):
                return JsonResponse({"error": "请勿重复提交"}, status=409)

        response = self.get_response(request)
        return response
