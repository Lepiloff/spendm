# Generated by Django 2.2.9 on 2020-06-01 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0063_auto_20200530_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfis',
            name='rfi_status',
            field=models.CharField(choices=[('Created', 'Created'), ('Opened', 'Opened'), ('Issued', 'Issued'), ('Closed', 'Closed')], default='Created', max_length=50),
        ),
    ]