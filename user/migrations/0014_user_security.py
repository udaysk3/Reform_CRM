# Generated by Django 5.0.1 on 2024-10-23 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_user_globals'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='security',
            field=models.BooleanField(default=False),
        ),
    ]
