# Generated by Django 5.0.1 on 2024-11-20 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_app', '0004_alter_customers_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='epc_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
