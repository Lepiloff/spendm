# Generated by Django 2.2.9 on 2020-04-04 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0022_auto_20200403_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendorcontacts',
            name='email',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]
