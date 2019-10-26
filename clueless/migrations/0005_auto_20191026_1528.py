# Generated by Django 2.2.5 on 2019-10-26 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clueless', '0004_auto_20191026_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='clueless.Player'),
        ),
        migrations.AlterField(
            model_name='casefile',
            name='characterCard',
            field=models.ForeignKey(limit_choices_to={'cardType': 'character'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='casefile_character_card', to='clueless.Card'),
        ),
        migrations.AlterField(
            model_name='casefile',
            name='roomCard',
            field=models.ForeignKey(limit_choices_to={'cardType': 'room'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='casefile_room_card', to='clueless.Card'),
        ),
        migrations.AlterField(
            model_name='casefile',
            name='weaponCard',
            field=models.ForeignKey(limit_choices_to={'cardType': 'weapon'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='casefile_weapon_card', to='clueless.Card'),
        ),
        migrations.AlterField(
            model_name='game',
            name='currentPlayer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='current_player_turn', to='clueless.Player'),
        ),
        migrations.AlterField(
            model_name='game',
            name='solution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='clueless.CaseFile'),
        ),
    ]
