# Generated by Django 4.2.1 on 2024-02-25 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("room", "0012_room_owner"),
    ]

    operations = [
        migrations.RenameField(
            model_name="room",
            old_name="owner",
            new_name="created_by",
        ),
    ]
