# Generated by Django 4.2.1 on 2023-10-11 06:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0024_trendingmessage_userliked"),
    ]

    operations = [
        migrations.AddField(
            model_name="trendingmessage",
            name="viewed",
            field=models.ManyToManyField(
                related_name="viewed", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
