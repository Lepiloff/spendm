# Generated by Django 2.2.9 on 2020-05-07 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0045_auto_20200507_0714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfiparticipationstatus',
            name='status',
            field=models.CharField(choices=[('Invited', 'Invited'), ('Accepted', 'Accepted'), ('Declined', 'Declined'), ('RFI Created', 'RFI Created'), ('RFI Outstanding', 'RFI Outstanding'), ('Received', 'Received'), ('Scored', 'Scored'), ('Closed', 'Closed')], default='Invited', max_length=50),
        ),
    ]
