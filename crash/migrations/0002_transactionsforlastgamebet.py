# Generated by Django 4.2.4 on 2023-10-11 12:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionsForLastGameBet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balloon_betted_on', models.CharField(default='', max_length=200)),
                ('game_id', models.CharField(max_length=200)),
                ('game_set_id', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('game_played', models.BooleanField(default=False)),
                ('bet_placed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
