# Generated by Django 4.2.1 on 2024-02-17 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0004_remove_conversation_converseuser_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="conversationmessage",
            options={"ordering": ("-created_at",)},
        ),
    ]
