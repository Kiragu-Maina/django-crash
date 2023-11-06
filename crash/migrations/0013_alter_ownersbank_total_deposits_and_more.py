# Generated by Django 4.2.4 on 2023-11-06 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0012_whoisadmin_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownersbank',
            name='total_deposits',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50, null=True),
        ),
        migrations.AlterField(
            model_name='ownersbank',
            name='total_withdrawals',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=50, null=True),
        ),
    ]
