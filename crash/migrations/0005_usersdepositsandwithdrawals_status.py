# Generated by Django 4.2.4 on 2023-11-02 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0004_usersdepositsandwithdrawals_charges_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersdepositsandwithdrawals',
            name='status',
            field=models.CharField(default=''),
        ),
    ]
