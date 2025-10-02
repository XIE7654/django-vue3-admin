from datetime import datetime
from django.core.management.base import BaseCommand
from system.models import Menu, MenuMeta

from utils.string_utils import camel_to_snake

"""
自动生成 菜单 代码的 Django 管理命令
使用方法: python manage.py gen_menu_json <app> <model> <parent>
system 是 app 名称, Config 是 model 名称, System 是上级菜单名称
例如: python manage.py gen_menu_json --app system --model Config --parent System
"""

# gen_menu_json --app system --model Config --parent 系统管理
def gen_menu(app_name, model_name, parent_menu_name, creator='admin'):
    print(parent_menu_name, 'parent')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_iso = datetime.now().isoformat()
    model_lower = camel_to_snake(model_name)
    model_title = model_name.capitalize()

    # 查找父菜单对象
    parent_menu = Menu.objects.filter(name=parent_menu_name).first()
    parent_id = parent_menu.id if parent_menu else None

    # 创建主菜单的元数据
    meta = MenuMeta.objects.create(
        title=f"{app_name}.{model_lower}.title",
        icon="",
        sort=0,
        affix_tab=False,
        badge="",
        badge_type="",
        badge_variants="",
        iframe_src="",
        link=""
    )

    # 创建主菜单
    page_menu_obj = Menu.objects.create(
        pid=parent_menu,
        name=model_title,
        status=1,
        type="menu",
        sort=100,
        path=f"/{app_name}/{model_lower}",
        component=f"/{app_name}/{model_lower}/list",
        auth_code="",
        meta=meta
    )

    # 按钮权限
    buttons = [
        {"name": "Create", "title": "common.create", "auth_code": f"{app_name}:{model_lower}:create"},
        {"name": "Edit", "title": "common.edit", "auth_code": f"{app_name}:{model_lower}:edit"},
        {"name": "Delete", "title": "common.delete", "auth_code": f"{app_name}:{model_lower}:delete"},
        {"name": "Query", "title": "common.query", "auth_code": f"{app_name}:{model_lower}:query"},
        {"name": "Query", "title": "common.query", "auth_code": f"{app_name}:{model_lower}:import"},
        {"name": "Query", "title": "common.query", "auth_code": f"{app_name}:{model_lower}:export"},
    ]
    for idx, btn in enumerate(buttons):
        btn_meta = MenuMeta.objects.create(
            title=btn["title"],
            icon="",
            sort=0,
            affix_tab=False,
            badge="",
            badge_type="",
            badge_variants="",
            iframe_src="",
            link=""
        )
        Menu.objects.create(
            pid=page_menu_obj,
            name=f"{model_title}{btn['name']}",
            status=1,
            type="button",
            sort=idx,
            path="",
            component="",
            auth_code=btn["auth_code"],
            meta=btn_meta
        )

    return page_menu_obj

class Command(BaseCommand):
    help = '自动生成菜单和按钮权限结构，并写入Menu模型'

    def add_arguments(self, parser):
        parser.add_argument('--app', required=True, help='app名称')
        parser.add_argument('--model', required=True, help='model名称')
        parser.add_argument('--parent', required=True, help='上级菜单名称')

    def handle(self, *args, **options):
        app = options['app']
        model = options['model']
        parent = options['parent']
        try:
            menu = gen_menu(app, model, parent)
            self.stdout.write(self.style.SUCCESS(f"菜单 {menu.name} 及其按钮权限已写入数据库 (id={menu.id})"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e))) 