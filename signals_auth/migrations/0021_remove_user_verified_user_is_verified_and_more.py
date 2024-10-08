# Generated by Django 5.0.7 on 2024-08-23 15:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0020_alter_mt5account_symbols_group_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="verified",
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="OneTimePassowrd",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("otp", models.CharField(max_length=6)),
                (
                    "user",
                    models.OneToOneField(
                        default=None,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
