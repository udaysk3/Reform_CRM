# Generated by Django 5.0.1 on 2024-11-15 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_app', '0003_answer_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customers',
            name='phone_number',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]