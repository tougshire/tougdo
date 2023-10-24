# Generated by Django 4.2.4 on 2023-10-22 15:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tougdo", "0011_delete_null_tag_slugs"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tag",
            name="title",
        ),
        migrations.AlterField(
            model_name="tag",
            name="slug",
            field=models.SlugField(verbose_name="slug"),
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(
                fields=("owner", "slug"), name="owner_slug_uniqueconstraint"
            ),
        ),
    ]