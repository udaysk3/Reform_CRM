# Generated by Django 5.0.1 on 2024-11-05 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_actions_requirements_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='parameter',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
        migrations.AlterField(
            model_name='questions',
            name='question',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
        migrations.AlterField(
            model_name='questions',
            name='type',
            field=models.CharField(blank=True, max_length=9999, null=True),
        ),
    ]
