__all__ = [
    'DeptViewSet',
    'MenuViewSet',
    'MenuMetaViewSet',
    'RoleViewSet',
    'DictDataViewSet',
    'DictTypeViewSet',
    'PostViewSet',
    'UserViewSet',
    'ConfigViewSet',
    'LoginLogViewSet',
]

from system.views.dict_data import DictDataViewSet
from system.views.dict_type import DictTypeViewSet
from system.views.menu import MenuViewSet, MenuMetaViewSet
from system.views.role import RoleViewSet

from system.views.dept import DeptViewSet
from system.views.post import PostViewSet
from system.views.login_log import LoginLogViewSet
from system.views.config import ConfigViewSet
from system.views.user import *