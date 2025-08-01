# Generated by Django 5.2.1 on 2025-07-21 03:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0004_alter_chatconversation_model_id_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "remark",
                    models.CharField(
                        blank=True,
                        db_comment="备注",
                        help_text="备注",
                        max_length=256,
                        null=True,
                        verbose_name="备注",
                    ),
                ),
                (
                    "creator",
                    models.CharField(
                        blank=True,
                        db_comment="创建人",
                        help_text="创建人",
                        max_length=64,
                        null=True,
                        verbose_name="创建人",
                    ),
                ),
                (
                    "modifier",
                    models.CharField(
                        blank=True,
                        db_comment="修改人",
                        help_text="修改人",
                        max_length=64,
                        null=True,
                        verbose_name="修改人",
                    ),
                ),
                (
                    "update_time",
                    models.DateTimeField(
                        auto_now=True,
                        db_comment="修改时间",
                        help_text="修改时间",
                        null=True,
                        verbose_name="修改时间",
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_comment="创建时间",
                        help_text="创建时间",
                        null=True,
                        verbose_name="创建时间",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        db_comment="是否软删除",
                        default=False,
                        verbose_name="是否软删除",
                    ),
                ),
                (
                    "public_status",
                    models.BooleanField(default=False, verbose_name="是否发布"),
                ),
                ("platform", models.CharField(max_length=64, verbose_name="平台")),
                ("model", models.CharField(max_length=64, verbose_name="模型")),
                ("prompt", models.TextField(max_length=2000, verbose_name="提示词")),
                ("width", models.IntegerField(verbose_name="图片宽度")),
                ("height", models.IntegerField(verbose_name="图片高度")),
                ("options", models.JSONField(null=True, verbose_name="绘制参数")),
                ("status", models.CharField(max_length=20, verbose_name="绘画状态")),
                (
                    "pic_url",
                    models.URLField(
                        max_length=2048, null=True, verbose_name="图片地址"
                    ),
                ),
                (
                    "error_message",
                    models.CharField(
                        max_length=1024, null=True, verbose_name="错误信息"
                    ),
                ),
                (
                    "task_id",
                    models.CharField(
                        max_length=1024, null=True, verbose_name="任务编号"
                    ),
                ),
                (
                    "buttons",
                    models.CharField(
                        max_length=2048, null=True, verbose_name="mj buttons 按钮"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_comment="用户编号",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "AI 绘画表",
                "verbose_name_plural": "AI 绘画表",
                "db_table": "ai_image",
            },
        ),
    ]
