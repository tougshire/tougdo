from django.db import migrations


def create_priorities(apps, schema_editor):
    Priority = apps.get_model("tougdo", "Priority")
    for pridata in [
        {
            "number": 1,
            "label": "Highest",
            "description": "terrible consequences if not done",
        },
        {
            "number": 2,
            "label": "High",
            "description": "difficult consequences if not done",
        },
        {
            "number": 3,
            "label": "Medium",
            "description": "unconfortable consequences if not done",
        },
        {
            "number": 4,
            "label": "Low",
            "description": "minor consequences if not done",
        },
        {
            "number": 5,
            "label": "Lowest",
            "description": "almost no consequence if not done",
        },
    ]:
        Priority.objects.create(
            number=pridata["number"],
            label=pridata["label"],
            description=pridata["description"],
        )


class Migration(migrations.Migration):
    dependencies = [
        ("tougdo", "0007_priority_item_priority"),
    ]

    operations = [
        migrations.RunPython(create_priorities),
    ]
