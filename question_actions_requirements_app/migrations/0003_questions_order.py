# Generated by Django 5.0.1 on 2024-11-08 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_actions_requirements_app', '0002_alter_questions_parameter_alter_questions_question_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]