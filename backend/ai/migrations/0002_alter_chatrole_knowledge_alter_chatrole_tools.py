# Generated by Django 5.2.1 on 2025-07-13 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatrole',
            name='knowledge',
            field=models.ManyToManyField(blank=True, related_name='roles', to='ai.knowledge', verbose_name='关联的知识库'),
        ),
        migrations.AlterField(
            model_name='chatrole',
            name='tools',
            field=models.ManyToManyField(blank=True, related_name='roles', to='ai.tool', verbose_name='关联的工具'),
        ),
    ]
