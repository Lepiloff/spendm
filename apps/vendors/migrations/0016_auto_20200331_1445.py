# Generated by Django 2.2.9 on 2020-03-31 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0015_auto_20200331_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfiparticipation',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]