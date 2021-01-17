# Generated by Django 3.1.5 on 2021-01-16 18:04

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('risla', '0002_auto_20210101_0725'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='person',
            managers=[
                ('random_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='person',
            name='bplace_country',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='dplace_country',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='dplace_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='occupation',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=models.CharField(max_length=75, null=True),
        ),
    ]