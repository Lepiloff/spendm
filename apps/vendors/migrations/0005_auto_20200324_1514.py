# Generated by Django 2.2.9 on 2020-03-24 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0004_auto_20200324_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfis',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]