# Generated by Django 5.0.4 on 2024-06-24 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0005_mt5account_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="mt5account",
            name="master",
            field=models.BooleanField(default=False),
        ),
    ]
