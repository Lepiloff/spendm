# Generated by Django 2.2.9 on 2020-05-27 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0056_elements_initialize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='subcategories',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
