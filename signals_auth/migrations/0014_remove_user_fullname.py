# Generated by Django 5.0.6 on 2024-07-05 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0013_alter_user_first_name_alter_user_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="fullname",
        ),
    ]
