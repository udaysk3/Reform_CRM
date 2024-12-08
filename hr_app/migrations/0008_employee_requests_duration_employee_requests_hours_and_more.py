# Generated by Django 5.0.1 on 2024-11-02 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr_app', '0007_employee_compassionate_employee_duvey_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='requests_duration',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='requests_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='requests_leave_file',
            field=models.FileField(blank=True, null=True, upload_to='leave_files'),
        ),
        migrations.AddField(
            model_name='employee',
            name='requests_leave_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='requests_status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_accrued',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_beginning_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_current_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_scheduled',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_summary_leave_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='time_off_used',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='upcoming_duration',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='upcoming_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='upcoming_leave_file',
            field=models.FileField(blank=True, null=True, upload_to='leave_files'),
        ),
        migrations.AddField(
            model_name='employee',
            name='upcoming_leave_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='upcoming_status',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
