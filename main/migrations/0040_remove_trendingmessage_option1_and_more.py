# Generated by Django 4.2.1 on 2024-03-28 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0039_alter_trendingmessage_voted"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trendingmessage",
            name="option1",
        ),
        migrations.RemoveField(
            model_name="trendingmessage",
            name="option2",
        ),
        migrations.RemoveField(
            model_name="trendingmessage",
            name="voted",
        ),
        migrations.RemoveField(
            model_name="trendingmessage",
            name="votes_option1",
        ),
        migrations.RemoveField(
            model_name="trendingmessage",
            name="votes_option2",
        ),
    ]
