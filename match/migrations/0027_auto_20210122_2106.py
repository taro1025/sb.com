# Generated by Django 3.1.4 on 2021-01-22 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0026_user_notice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='describe1',
            field=models.TextField(blank=True, null=True, verbose_name='コース1の説明'),
        ),
        migrations.AlterField(
            model_name='user',
            name='describe2',
            field=models.TextField(blank=True, null=True, verbose_name='コース2の説明'),
        ),
        migrations.AlterField(
            model_name='user',
            name='describe3',
            field=models.TextField(blank=True, null=True, verbose_name='コース3の説明'),
        ),
    ]
