# Generated by Django 4.2.1 on 2023-10-05 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0020_alter_trendingmessage_view_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="trendingmessage",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
