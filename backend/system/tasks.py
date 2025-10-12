import requests

from celery import shared_task
from system.models import LoginLog, User


@shared_task
def add(x, y):
    return x + y


@shared_task
def update_user_login_info(username, client_ip, user_agent, result):
    # 获取地理位置信息
    location_info = get_location_from_ip(client_ip)
    # 记录登录日录
    LoginLog.objects.create(
        username=username,
        result=result,
        user_ip=client_ip,
        location=location_info,
        user_agent=user_agent
    )

def get_location_from_ip(ip):
    """根据IP地址获取地理位置信息"""
    try:
        if ip in ['127.0.0.1', 'localhost']:
            return "本地网络"

        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data["status"] == "success":
                location_parts = [data["city"], data["regionName"], data["country"]]
                return ', '.join(location_parts) if location_parts else "未知位置"
            else:
                return "位置获取失败"
                # return f"IP {ip} 查询失败：{data['message']}"
        except Exception as e:
            return "位置获取失败"
            # return f"IP {ip} 连接错误：{str(e)}"
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取IP地址位置信息失败: {str(e)}")
        return "位置获取失败"