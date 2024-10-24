# Generated by Django 5.0.1 on 2024-10-13 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_user_funding_route'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='archive',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='client',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='product',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='stage',
            field=models.BooleanField(default=False),
        ),
    ]
