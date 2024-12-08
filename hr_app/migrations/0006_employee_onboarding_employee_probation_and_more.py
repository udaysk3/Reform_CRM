# Generated by Django 5.0.1 on 2024-11-02 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0005_alter_employee_reporting_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='onboarding',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='probation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='regularised',
            field=models.DateField(blank=True, null=True),
        ),
    ]
