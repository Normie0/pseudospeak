# Generated by Django 4.2.1 on 2023-09-14 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_alter_trendingmessage_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="trendingmessage",
            options={"ordering": ("-date_added",)},
        ),
    ]
