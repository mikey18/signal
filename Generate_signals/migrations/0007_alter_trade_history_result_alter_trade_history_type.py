# Generated by Django 5.0.7 on 2024-08-25 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Generate_signals", "0006_trade_history_balance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trade_history",
            name="result",
            field=models.CharField(
                blank=True,
                choices=[("profit", "profit"), ("loss", "loss")],
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="trade_history",
            name="type",
            field=models.CharField(
                choices=[("BUY", "BUY"), ("SELL", "SELL")], max_length=100
            ),
        ),
    ]
