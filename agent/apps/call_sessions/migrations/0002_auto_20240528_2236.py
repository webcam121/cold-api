# Generated by Django 3.1.6 on 2024-05-28 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call_sessions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='callsession',
            name='user',
        ),
        migrations.AddField(
            model_name='callsession',
            name='phone_number',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
