# Generated by Django 5.0.1 on 2024-10-22 09:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_archive_user_client_user_product_user_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='satatus',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='user',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='client',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='customer',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='dashboard',
            field=models.BooleanField(default=False),
        ),
    ]
