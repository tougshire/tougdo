# Generated by Django 4.2.4 on 2023-10-17 01:29

from django.db import migrations, models
import tougdo.models


class Migration(migrations.Migration):

    dependencies = [
        ('tougdo', '0005_item_done_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, null=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='item',
            name='done_date',
            field=models.DateField(blank=True, null=True, verbose_name='is done'),
        ),
        migrations.AlterField(
            model_name='item',
            name='due_date',
            field=models.DateField(default=tougdo.models.one_week_hence),
        ),
    ]
