# Generated by Django 2.2.9 on 2020-04-24 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0036_auto_20200423_1554'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companygeneralinfoquestion',
            old_name='statement',
            new_name='question',
        ),
    ]