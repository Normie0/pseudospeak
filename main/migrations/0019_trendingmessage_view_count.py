# Generated by Django 4.2.1 on 2023-09-21 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0018_alter_hashtag_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="trendingmessage",
            name="view_count",
            field=models.IntegerField(null=True),
        ),
    ]
