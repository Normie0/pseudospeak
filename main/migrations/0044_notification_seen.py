# Generated by Django 4.2.1 on 2024-04-09 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0043_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="seen",
            field=models.BooleanField(default=False),
        ),
    ]
