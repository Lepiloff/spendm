# Generated by Django 2.2.9 on 2020-05-18 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0048_auto_20200513_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentcategories',
            name='parent_category_name',
            field=models.CharField(choices=[('COMMON S2P', 'COMMON S2P'), ('COMMON SOURCING – SXM', 'COMMON SOURCING – SXM'), ('SERVICES', 'SERVICES'), ('SOURCING', 'SOURCING'), ('SXM', 'SXM'), ('Spend Analytics', 'Spend Analytics'), ('CLM', 'CLM'), ('eProcurement', 'eProcurement'), ('I2P', 'I2P')], max_length=45, unique=True),
        ),
    ]