#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动生成 CRUD 代码的 Django 管理命令
使用方法: python manage.py generate_crud <app_name> <model_name>
例如: python manage.py generate_crud system Dept
"""

import os
from string import Template
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import models

from utils.string_utils import camel_to_snake

TPL_DIR = os.path.join(os.path.dirname(__file__), 'tpl')

def render_tpl(tpl_name, context):
    tpl_path = os.path.join(TPL_DIR, tpl_name)
    with open(tpl_path, 'r', encoding='utf-8') as f:
        tpl = Template(f.read())
    return tpl.substitute(context)


def ensure_view_dirs(app_name, model_name_snake):
    base_dir = f'../web/apps/web-antd/src/views/{app_name.lower()}'
    model_dir = os.path.join(base_dir, model_name_snake)
    if not os.path.exists(base_dir):
        os.makedirs(model_dir, exist_ok=True)
    else:
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)

def capitalize_first(s):
    return s[:1].upper() + s[1:] if s else s

def camel_case(s):
    return ''.join(word.capitalize() for word in s.split('_'))

def get_context(app_name, model_name, model, model_name_snake):
    return {
        'model_name': model_name,
        'app_name': app_name,
        'app_name_camel': camel_case(app_name),
        'model_name_lower': model_name.lower(),
        'model_name_snake': model_name_snake,
        'verbose_name': model._meta.verbose_name or model_name,
    }

class Command(BaseCommand):
    help = '根据模型自动生成 CRUD 代码（后端视图 + 前端页面 + 模型）'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='应用名称')
        parser.add_argument('model_name', type=str, help='模型名称')
        parser.add_argument(
            '--frontend',
            action='store_true',
            help='是否同时生成前端代码',
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        model_name = options['model_name']
        model_name_snake = camel_to_snake(model_name)
        generate_frontend = options.get('frontend', False)

        try:
            # 获取模型
            model = apps.get_model(app_name, model_name)
        except LookupError:
            raise CommandError(f'模型 {app_name}.{model_name} 不存在')

        # 生成后端代码
        self.generate_backend_code(app_name, model_name, model, model_name_snake)
        
        if generate_frontend:
            # 生成前端代码
            self.generate_frontend_code(app_name, model_name, model, model_name_snake)

        self.stdout.write(
            self.style.SUCCESS(f'成功生成 {app_name}.{model_name} 的 CRUD 代码')
        )

    def generate_backend_code(self, app_name, model_name, model, model_name_snake):
        """生成后端代码"""
        # 生成视图集
        self.generate_viewset(app_name, model_name, model, model_name_snake)

    def generate_viewset(self, app_name, model_name, model, model_name_snake):
        """生成视图集"""
        filter_fields = []
        for field in model._meta.fields:
            if isinstance(field, (models.CharField, models.IntegerField, models.BooleanField)):
                filter_fields.append(f"'{field.name}'")
        
        context = get_context(app_name, model_name, model, model_name_snake)
        context['filterset_fields'] = ', '.join(filter_fields)
        viewset_code = render_tpl('viewset.py.tpl', context)
        
        viewset_path = f'{app_name}/views/{model_name_snake}.py'
        os.makedirs(os.path.dirname(viewset_path), exist_ok=True)
        
        with open(viewset_path, 'w', encoding='utf-8') as f:
            f.write(viewset_code)
        
        self.stdout.write(f'生成视图集: {viewset_path}')

    def generate_frontend_code(self, app_name, model_name, model, model_name_snake):
        ensure_view_dirs(app_name, model_name_snake)
        self.generate_frontend_model(app_name, model_name, model, model_name_snake)
        self.generate_frontend_list(app_name, model_name, model, model_name_snake)
        self.generate_frontend_data(app_name, model_name, model, model_name_snake)
        self.generate_frontend_form_component(app_name, model_name, model, model_name_snake)

    def generate_frontend_model(self, app_name, model_name, model, model_name_snake):
        """生成前端模型定义"""
        interface_fields = []
        for field in model._meta.fields:
            field_type = self.get_typescript_type(field)
            interface_fields.append(f'    {field.name}: {field_type};')
        
        interface_content = '\n'.join(interface_fields)
        
        context = get_context(app_name, model_name, model, model_name_snake)
        context['interface_fields'] = interface_content
        model_code = render_tpl('frontend_model.ts.tpl', context)
        
        model_path = f'../web/apps/web-antd/src/models/{app_name.lower()}/{model_name_snake}.ts'
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(model_code)
        
        self.stdout.write(f'生成前端模型: {model_path}')

    def generate_frontend_list(self, app_name, model_name, model, model_name_snake):
        context = get_context(app_name, model_name, model, model_name_snake)
        list_code = render_tpl('frontend_list.vue.tpl', context)
        list_path = f'../web/apps/web-antd/src/views/{app_name.lower()}/{model_name_snake}/list.vue'
        with open(list_path, 'w', encoding='utf-8') as f:
            f.write(list_code)
        self.stdout.write(f'生成前端列表页面: {list_path}')

    def generate_frontend_data(self, app_name, model_name, model, model_name_snake):
        CORE_FIELDS = ['create_time', 'update_time', 'creator', 'modifier', 'is_deleted', 'remark']
        business_fields = []
        core_fields = []
        for field in model._meta.fields:
            if field.name in CORE_FIELDS:
                core_fields.append(field)
            else:
                business_fields.append(field)
        # 生成 useSchema
        form_fields = []
        for field in business_fields + core_fields:
            if field.name in ['id', 'create_time', 'update_time', 'creator', 'modifier', 'is_deleted']:
                continue  # 这些一般不在表单里
            field_config = self.generate_form_field(field)
            if field_config:
                form_fields.append(field_config)

        # useGridFormSchema
        grid_form_fields = []
        for field in business_fields:
            if field.name in ['id']:
                continue
            field_config = self.generate_grid_form_field(field)
            if field_config:
                grid_form_fields.append(field_config)

        # 生成 useColumns
        columns = self.get_columns_code(business_fields + core_fields)
        context = get_context(app_name, model_name, model, model_name_snake)
        context['form_fields'] = '\n'.join(form_fields)
        context['grid_form_fields'] = '\n'.join(grid_form_fields)
        context['columns'] = '\n'.join(columns)
        data_path = f'../web/apps/web-antd/src/views/{app_name.lower()}/{model_name_snake}/data.ts'
        data_code = render_tpl('frontend_data.ts.tpl', context)
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(data_code)
        self.stdout.write(f'生成前端表单配置: {data_path}')

    def generate_frontend_form_component(self, app_name, model_name, model, model_name_snake):
        ensure_view_dirs(app_name, model_name_snake)
        context = get_context(app_name, model_name, model, model_name_snake)
        form_path = f'../web/apps/web-antd/src/views/{app_name.lower()}/{model_name_snake}/modules/form.vue'
        form_code = render_tpl('frontend_form.vue.tpl', context)
        os.makedirs(os.path.dirname(form_path), exist_ok=True)
        with open(form_path, 'w', encoding='utf-8') as f:
            f.write(form_code)
        self.stdout.write(f'生成前端表单组件: {form_path}')

    def get_typescript_type(self, field):
        """获取 TypeScript 类型"""
        if isinstance(field, models.CharField):
            return 'string'
        elif isinstance(field, models.TextField):
            return 'string'
        elif isinstance(field, models.IntegerField):
            return 'number'
        elif isinstance(field, models.BooleanField):
            return 'boolean'
        elif isinstance(field, models.DateTimeField):
            return 'string'
        elif isinstance(field, models.DateField):
            return 'string'
        elif isinstance(field, models.ForeignKey):
            return 'number'
        else:
            return 'any'

    def generate_form_field(self, field):
        field_name = field.name
        field_label = getattr(field, 'verbose_name', field_name)
        if field_name == 'status':
            return f'''    {{
      component: 'RadioGroup',
      componentProps: {{
        buttonStyle: 'solid',
        options: [
          {{ label: $t('common.enabled'), value: 1 }},
          {{ label: $t('common.disabled'), value: 0 }},
        ],
        optionType: 'button',
      }},
      defaultValue: 1,
      fieldName: 'status',
      label: $t('system.status'),
    }},'''
        if isinstance(field, models.CharField):
            return f'''    {{
      component: 'Input',
      fieldName: '{field_name}',
      label: '{field_label}',
      rules: z.string().min(1, $t('ui.formRules.required', ['{field_label}'])).max(100, $t('ui.formRules.maxLength', ['{field_label}', 100])),
    }},'''
        elif isinstance(field, models.TextField):
            return f'''    {{
      component: 'Input',
      componentProps: {{ rows: 3, showCount: true }},
      fieldName: '{field_name}',
      label: '{field_label}',
      rules: z.string().max(500, $t('ui.formRules.maxLength', ['{field_label}', 500])).optional(),
    }},'''
        elif isinstance(field, models.IntegerField):
            return f'''    {{
      component: 'InputNumber',
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''
        elif isinstance(field, models.BooleanField):
            return f'''    {{
      component: 'RadioGroup',
      componentProps: {{
        buttonStyle: 'solid',
        options: [
          {{ label: '开启', value: 1 }},
          {{ label: '关闭', value: 0 }},
        ],
        optionType: 'button',
      }},
      defaultValue: 1,
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''
        else:
            return f'''    {{
      component: 'Input',
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''

    def generate_grid_form_field(self, field):
        field_name = field.name
        field_label = getattr(field, 'verbose_name', field_name)
        if field_name == 'status':
            return f'''    {{
      component: 'Select',
      fieldName: 'status',
      label: '状态',
      componentProps: {{
        allowClear: true,
        options: [
          {{ label: '启用', value: 1 }},
          {{ label: '禁用', value: 0 }},
        ],
      }},
    }},'''
        if isinstance(field, models.CharField):
            return f'''    {{
      component: 'Input',
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''
        elif isinstance(field, models.IntegerField):
            return f'''    {{
      component: 'InputNumber',
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''
        else:
            return f'''    {{
      component: 'Input',
      fieldName: '{field_name}',
      label: '{field_label}',
    }},'''

    def get_columns_code(self, fields):
        columns = []
        for field in fields:
            if field.name == 'status':
                columns.append(
                    """    {
      field: 'status',
      title: '状态',
      cellRender: { name: 'CellTag' },
    },"""
                )
                continue
            if isinstance(field, (models.DateField, models.DateTimeField)):
                columns.append(
                    f"""    {{
      field: '{field.name}',
      title: '{getattr(field, 'verbose_name', field.name)}',
      width: 150,
      formatter: ({{ cellValue }}) => format_datetime(cellValue),
    }},"""
                )
                continue
            columns.append(
                f"""    {{
      field: '{field.name}',
      title: '{getattr(field, 'verbose_name', field.name)}',
    }},"""
            )
        return columns