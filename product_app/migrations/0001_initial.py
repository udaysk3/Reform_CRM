# Generated by Django 5.0.1 on 2024-10-09 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0001_initial'),
        ('region_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=999, null=True)),
                ('global_archive', models.BooleanField(default=False)),
                ('council', models.ManyToManyField(related_name='product', to='region_app.councils')),
                ('documents', models.ManyToManyField(related_name='product', to='home.document')),
                ('stage', models.ManyToManyField(related_name='product', to='home.stage')),
            ],
        ),
    ]