import hashlib
from django.core.cache import cache

def generate_idempotency_key(user_id, path, body):
    """
    生成幂等性检查的唯一标识key
    :param user_id: 用户ID或"anonymous"
    :param path: 请求路径
    :param body: 请求体内容
    :return: MD5哈希值作为唯一标识
    """
    return hashlib.md5(f"{user_id}_{path}_{body}".encode()).hexdigest()

def check_idempotency(key, timeout=10):
    """
    检查是否为重复请求
    :param key: 幂等性标识key
    :param timeout: 缓存超时时间(秒)
    :return: True表示重复请求，False表示首次请求
    """
    if cache.get(key):
        return True
    cache.set(key, "processing", timeout)
    return False

def get_user_identifier(request):
    """
    获取用户标识符
    :param request: HTTP请求对象
    :return: 用户ID或"anonymous"
    """
    return request.user.id if request.user.is_authenticated else "anonymous"
