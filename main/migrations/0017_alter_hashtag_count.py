# Generated by Django 4.2.1 on 2023-09-21 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0016_alter_hashtag_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hashtag",
            name="count",
            field=models.IntegerField(default=1, null=True),
        ),
    ]
