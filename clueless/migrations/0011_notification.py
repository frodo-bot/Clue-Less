# Generated by Django 2.2.5 on 2019-11-06 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clueless', '0010_auto_20191102_1308'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500)),
            ],
        ),
    ]
