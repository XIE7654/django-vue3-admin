import pandas as pd
from django.core.management.base import BaseCommand
from system.models import CityArea


class Command(BaseCommand):
    help = '导入省市区数据'

    def handle(self, *args, **options):
        file_path = 'data/省市区.xlsx'  # 文件路径，根据实际情况调整
        try:
            # 读取 Excel 文件
            excel_file = pd.ExcelFile(file_path)
            df = excel_file.parse()  # 假设只有一个工作表，如果有多个，需要调整

            # 使用 bulk_create 进行批量导入
            bulk_objects = []
            for index, row in df.iterrows():
                bulk_objects.append(CityArea(
                    prov_id=row['省份ID'],
                    prov_name=row['省份名称'],
                    city_id=row['城市ID'],
                    city_name=row['城市名称'],
                    area_id=row['地区ID'],
                    area_name=row['地区名称']
                ))

            # 批量创建对象
            CityArea.objects.bulk_create(bulk_objects, batch_size=1000)

            self.stdout.write(self.style.SUCCESS('数据导入成功'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'文件 {file_path} 未找到'))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'列 {e} 未找到'))