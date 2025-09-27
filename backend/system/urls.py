from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'dept', views.DeptViewSet)
router.register(r'menu-meta', views.MenuMetaViewSet)
router.register(r'menu', views.MenuViewSet)
router.register(r'role', views.RoleViewSet)
router.register(r'dict_data', views.DictDataViewSet)
router.register(r'dict_type', views.DictTypeViewSet)
router.register(r'post', views.PostViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'login_log', views.LoginLogViewSet)
router.register(r'config', views.ConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.user.UserLogin.as_view()),
    path('info/', views.user.UserInfo.as_view()),
    path('codes/', views.user.Codes.as_view()),
    path('logout/', views.user.Logout.as_view()),
]