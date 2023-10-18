# Generated by Django 4.2.4 on 2023-10-18 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tougdo', '0006_tag_slug_alter_item_done_date_alter_item_due_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True)),
                ('number', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='priority',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tougdo.priority'),
        ),
    ]
