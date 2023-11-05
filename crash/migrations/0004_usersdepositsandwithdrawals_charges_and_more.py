# Generated by Django 4.2.4 on 2023-11-02 04:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0003_rename_deposits_usersdepositsandwithdrawals_deposit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersdepositsandwithdrawals',
            name='charges',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='usersdepositsandwithdrawals',
            name='net_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='usersdepositsandwithdrawals',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='usersdepositsandwithdrawals',
            name='deposit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='usersdepositsandwithdrawals',
            name='withdrawal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
