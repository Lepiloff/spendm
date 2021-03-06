# Generated by Django 2.2.9 on 2020-05-29 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0061_merge_20200527_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parentcategories',
            name='modules',
        ),
        migrations.AlterField(
            model_name='modules',
            name='parent_categories',
            field=models.ManyToManyField(related_name='parent_categories', through='vendors.ModulesParentCategories', to='vendors.ParentCategories'),
        ),
    ]
