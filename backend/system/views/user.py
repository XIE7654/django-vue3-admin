import requests
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from system.tasks import update_user_login_info
from system.models import User, Menu, Dept
from utils.ip_utils import get_client_ip

from utils.serializers import CustomModelSerializer
from utils.custom_model_viewSet import CustomModelViewSet


class UserSerializer(CustomModelSerializer):
    roles = serializers.SerializerMethodField()  # 新增字段
    depts = serializers.SerializerMethodField()  # 新增字段
    """
    用户数据 序列化器
    """
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'create_time', 'update_time']

    def get_roles(self, obj):
        """
        返回用户所有角色的名称列表
        """
        return list(obj.role.values_list('name', flat=True))

    def get_depts(self, obj):
        # 返回所有部门名称列表
        return list(obj.dept.values_list('name', flat=True))

    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class UserLogin(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # 获取真实IP地址
        client_ip = get_client_ip(request)

        # 异步处理用户登录信息更新和日志记录
        update_user_login_info.delay(
            user.id,
            client_ip,
            request.META.get('HTTP_USER_AGENT', '')
        )

        user_data = UserSerializer(user).data
        # 在序列化后的数据中加入 accessToken
        user_data['accessToken'] = token.key
        return Response({
            "code": 0,
            "data": user_data,
            "error": None,
            "message": "ok"
        })

    def get_location_from_ip(self, ip):
        """根据IP地址获取地理位置信息"""
        try:
            # 对于本地IP地址，返回默认值
            if ip in ['127.0.0.1', 'localhost']:
                return "本地网络"

            # 查询IP地址信息
            # 免费接口，无需密钥，返回JSON格式数据
            url = f"http://ip-api.com/json/{ip}?lang=zh-CN"  # lang=zh-CN 确保返回中文
            try:
                response = requests.get(url, timeout=5)
                data = response.json()
                if data["status"] == "success":  # 接口返回成功
                    # 构建地区信息字符串
                    location_parts = [data["city"], data["regionName"],data["country"]]
                    return ', '.join(location_parts) if location_parts else "未知位置"
                else:
                    return f"IP {ip} 查询失败：{data['message']}"
            except Exception as e:
                return f"IP {ip} 连接错误：{str(e)}"
        except Exception as e:
            # 记录错误日志
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取IP地址位置信息失败: {str(e)}")
            return "位置获取失败"

class UserInfo(APIView):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_data = UserSerializer(user).data
        if user.is_superuser:
            roles = ['admin']
            # menus = Menu.objects.filter(pid__isnull=True).order_by('sort')
            permissions = Menu.objects.filter(type='button').order_by('auth_code').values_list('auth_code', flat=True)
        else:
            roles = user.get_role_name
            # menus = Menu.objects.filter(pid__isnull=True, role__users=user).order_by('sort').distinct()
            permissions = Menu.objects.filter(type='button', role__users=user).order_by('auth_code').distinct().values_list('auth_code', flat=True)
        # menus_data = MenuSerializer(menus, many=True).data
        user_data['roles'] = roles
        user_data['permissions'] = permissions
        return Response({
            "code": 0,
            "data": user_data,
            "error": None,
            "message": "ok"
        })


class Codes(APIView):

    def get(self, request, *args, **kwargs):
        return Response({
            "code": 0,
            "data": [
                "AC_100100",
                "AC_100110",
                "AC_100120",
                "AC_100010"
            ],
            "error": None,
            "message": "ok"
        })


class UserFilter(filters.FilterSet):
    # 多部门过滤，假设字段为 dept，支持 ?dept=1,2,3
    dept = filters.CharFilter(method='filter_dept')
    # 名称和手机号模糊查询
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    mobile = filters.CharFilter(field_name='mobile', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['dept', 'username', 'nickname', 'mobile', 'status']

    def filter_dept(self, queryset, name, value):
        # value 可能是单个id或逗号分隔的多个id
        dept_ids = [int(i) for i in value.split(',') if i]
        all_ids = set()
        for dept_id in dept_ids:
            all_ids.update(get_dept_and_children_ids(dept_id))
        return queryset.filter(dept__in=all_ids)

def get_dept_and_children_ids(dept_id):
    # 递归查找所有子部门id
    ids = [dept_id]
    children = Dept.objects.filter(pid_id=dept_id)
    for child in children:
        ids.extend(get_dept_and_children_ids(child.id))
    return ids

class UserViewSet(CustomModelViewSet):
    """
    用户数据 视图集
    """
    queryset = User.objects.filter(is_deleted=False).order_by('-id').prefetch_related('role', 'dept', 'post')
    serializer_class = UserSerializer
    read_only_fields = ['id', 'create_time', 'update_time', 'login_ip']
    filterset_class = UserFilter
    search_fields = ['username', 'nickname', 'mobile']  # 支持模糊搜索
    ordering_fields = ['create_time', 'id']
    ordering = ['-create_time']


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # user = request.user
        # 删除用户的Token
        # Token.objects.filter(user=user).delete()
        return Response({
            "code": 0,
            "data": None,
            "error": None,
            "message": "登出成功"
        })

