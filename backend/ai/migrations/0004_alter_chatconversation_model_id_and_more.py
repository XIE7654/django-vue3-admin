# Generated by Django 5.2.1 on 2025-07-17 07:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0003_aimodel_model_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatconversation",
            name="model_id",
            field=models.ForeignKey(
                blank=True,
                db_column="model_id",
                db_comment="向量模型编号",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ai.aimodel",
                verbose_name="向量模型编号",
            ),
        ),
        migrations.AlterField(
            model_name="chatmessage",
            name="model_id",
            field=models.ForeignKey(
                blank=True,
                db_column="model_id",
                db_comment="向量模型编号",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ai.aimodel",
                verbose_name="向量模型编号",
            ),
        ),
    ]
