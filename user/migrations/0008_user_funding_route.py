# Generated by Django 5.0.1 on 2024-04-02 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_rename_funding_route_user_council'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='funding_route',
            field=models.BooleanField(default=False),
        ),
    ]