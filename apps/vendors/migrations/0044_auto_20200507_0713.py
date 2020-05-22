# Generated by Django 2.2.9 on 2020-05-07 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0043_auto_20200424_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentcategories',
            name='parent_category_name',
            field=models.CharField(choices=[('COMMON S2P', 'COMMON S2P'), ('Common Sourcing - SXM', 'Common Sourcing - SXM'), ('Services', 'Services'), ('Sourcing', 'Sourcing'), ('SXM', 'SXM'), ('Spend Analytics', 'Spend Analytics'), ('CLM', 'CLM'), ('eProcurement', 'eProcurement'), ('I2P', 'I2P')], max_length=45, unique=True),
        ),
    ]