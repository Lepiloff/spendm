# Generated by Django 2.2.9 on 2020-04-02 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0018_historicalvendors_vendorid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendorcontacts',
            name='email',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
    ]