import pandas as pd

from rest_framework.decorators import action
from django.http import HttpResponse

class ExportMixin:
    """
    导出功能 Mixin，提供数据导出为 Excel 或 CSV 的功能
    """
    # 导出配置
    export_fields = {}  # 字段映射配置
    export_filename = None  # 导出文件名

    @action(detail=False, methods=['get'], url_path='export')
    def export_data(self, request):
        """
        导出数据功能
        支持通过参数控制导出字段:
        - fields: 指定要导出的字段，多个字段用逗号分隔
        - format: 导出格式 (excel/csv)，默认excel
        """
        # 获取查询集
        queryset = self.filter_queryset(self.get_queryset())

        # 获取导出字段配置
        export_config = self.get_export_fields(request)

        # 序列化数据
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # 处理数据
        processed_data = self.process_export_data(data, export_config)

        # 生成文件名
        filename = self.export_filename or f"{self.__class__.__name__}_export"

        # 根据格式返回响应
        export_format = request.query_params.get('format', 'excel').lower()

        if export_format == 'csv':
            return self.generate_csv_response(processed_data, filename)
        else:
            return self.generate_excel_response(processed_data, filename)

    def get_export_fields(self, request):
        """
        获取导出字段配置
        支持通过URL参数指定字段: ?fields=id,name,email
        """
        # 优先使用请求参数中的字段
        fields_param = request.query_params.get('fields')
        if fields_param:
            field_names = [f.strip() for f in fields_param.split(',')]
            # 只返回指定字段的配置
            return {field: self.export_fields.get(field, field) for field in field_names}
        # 默认返回所有配置字段
        return self.export_fields or {}

    def process_export_data(self, data, export_config):
        """
        处理导出数据，根据配置映射字段名和处理数据
        """
        if not export_config:
            return data

        processed_data = []
        for item in data:
            processed_item = {}
            for field_key, field_config in export_config.items():
                # field_config 可以是字符串(列名)或字典(包含列名和处理函数)
                if isinstance(field_config, dict):
                    column_name = field_config.get('name', field_key)
                    processor = field_config.get('processor')
                    value = item.get(field_key)
                    if processor and callable(processor):
                        value = processor(value, item)
                    processed_item[column_name] = value
                else:
                    # 简单映射
                    processed_item[field_config] = item.get(field_key, '')
            processed_data.append(processed_item)
        return processed_data

    def generate_excel_response(self, data, filename):
        """生成Excel格式响应"""
        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        df.to_excel(response, index=False)
        return response

    def generate_csv_response(self, data, filename):
        """生成CSV格式响应"""
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        df.to_csv(response, index=False)
        return response
