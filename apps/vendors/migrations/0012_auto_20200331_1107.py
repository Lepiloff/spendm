# Generated by Django 2.2.9 on 2020-03-31 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0011_auto_20200331_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendors',
            name='abr_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendors',
            name='office',
            field=models.CharField(default='', max_length=145),
        ),
    ]
