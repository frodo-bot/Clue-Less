# Generated by Django 2.2.5 on 2019-11-15 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clueless', '0018_game_disproveplayer'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='currentSuggestion',
            field=models.CharField(max_length=200, null=True),
        ),
    ]