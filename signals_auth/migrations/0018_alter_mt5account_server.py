# Generated by Django 5.0.6 on 2024-07-06 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals_auth', '0017_alter_mt5account_server'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mt5account',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signals_auth.brokers'),
        ),
    ]
