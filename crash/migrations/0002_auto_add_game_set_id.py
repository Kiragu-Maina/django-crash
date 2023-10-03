from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        # Your app's dependencies
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='game_set_id',
            field=models.CharField(default='', max_length=200),
        ),
    ]
