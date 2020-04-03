# Generated by Django 2.2.9 on 2020-04-02 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0019_auto_20200402_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalvendors',
            name='vendor_name',
            field=models.CharField(db_index=True, error_messages={'unique': 'Vendor already exists'}, max_length=45),
        ),
        migrations.AlterField(
            model_name='vendors',
            name='vendor_name',
            field=models.CharField(error_messages={'unique': 'Vendor already exists'}, max_length=45, unique=True),
        ),
    ]
