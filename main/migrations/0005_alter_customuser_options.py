# Generated by Django 4.2.3 on 2023-09-07 04:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={"permissions": [("can_view_customuser", "Can view custom user")]},
        ),
    ]
