# Generated by Django 2.2.9 on 2020-04-10 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0027_auto_20200410_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentcategories',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
