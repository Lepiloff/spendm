# Generated by Django 2.2.9 on 2020-03-28 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0009_auto_20200326_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfiparticipation',
            name='rfi',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='to_rfi', to='vendors.Rfis'),
        ),
    ]