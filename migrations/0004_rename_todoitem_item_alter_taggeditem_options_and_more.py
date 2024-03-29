# Generated by Django 4.2.4 on 2023-10-14 10:45

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tougdo", "0003_tag_taggeditem_remove_todomember_todo_item_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ToDoItem",
            new_name="Item",
        ),
        migrations.AlterModelOptions(
            name="taggeditem",
            options={"ordering": ["item"]},
        ),
        migrations.RenameField(
            model_name="taggeditem",
            old_name="todo_item",
            new_name="item",
        ),
    ]
