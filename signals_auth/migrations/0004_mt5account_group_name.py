# Generated by Django 5.0.4 on 2024-06-21 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0003_alter_mt5account_account"),
    ]

    operations = [
        migrations.AddField(
            model_name="mt5account",
            name="group_name",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
