# Generated by Django 5.0.1 on 2024-11-28 14:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0010_remove_clients_assigned_to_clients_assigned_to'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='clients',
            name='agent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients_as_agent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clients',
            name='client_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_user', to=settings.AUTH_USER_MODEL),
        ),
    ]