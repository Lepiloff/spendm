# Generated by Django 2.2.9 on 2020-04-13 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0031_auto_20200412_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modules',
            name='module_name',
            field=models.CharField(choices=[('Strategic Sourcing', 'Strategic Sourcing'), ('Supplier Management', 'Supplier Management'), ('Spend Analytics', 'Spend Analytics'), ('Contract Management', 'Contract Management'), ('e-Procurement', 'e-Procurement'), ('Invoice-to-Pay', 'Invoice-to-Pay'), ('Strategic Procurement', 'Strategic Procurement'), ('Technologies', 'Technologies'), ('Procure-to-Pay', 'Procure-to-Pay'), ('Source-to-Pay', 'Source-to-Pay')], max_length=50, unique=True),
        ),
    ]
