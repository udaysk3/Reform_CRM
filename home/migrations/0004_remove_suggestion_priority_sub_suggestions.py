# Generated by Django 5.0.1 on 2024-11-22 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_suggestion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suggestion',
            name='priority',
        ),
        migrations.CreateModel(
            name='Sub_suggestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=999, null=True)),
                ('suggestion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_suggestions', to='home.suggestion')),
            ],
        ),
    ]