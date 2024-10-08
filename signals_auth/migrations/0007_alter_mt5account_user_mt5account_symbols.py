# Generated by Django 5.0.6 on 2024-06-28 22:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0006_mt5account_master"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mt5account",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="MT5Account_Symbols",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "pair",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("EURUSD", "Euro/US Dollar"),
                            ("USDJPY", "US Dollar/Japanese Yen"),
                            ("GBPUSD", "British Pound/US Dollar"),
                            ("USDCHF", "US Dollar/Swiss Franc"),
                            ("USDCAD", "US Dollar/Canadian Dollar"),
                            ("AUDUSD", "Australian Dollar/US Dollar"),
                            ("NZDUSD", "New Zealand Dollar/US Dollar"),
                            ("EURGBP", "Euro/British Pound"),
                            ("EURJPY", "Euro/Japanese Yen"),
                            ("GBPJPY", "British Pound/Japanese Yen"),
                            ("AUDJPY", "Australian Dollar/Japanese Yen"),
                            ("NZDJPY", "New Zealand Dollar/Japanese Yen"),
                            ("AUDNZD", "Australian Dollar/New Zealand Dollar"),
                            ("AUDCAD", "Australian Dollar/Canadian Dollar"),
                            ("GBPAUD", "British Pound/Australian Dollar"),
                            ("GBPCAD", "British Pound/Canadian Dollar"),
                            ("EURAUD", "Euro/Australian Dollar"),
                            ("USDSGD", "US Dollar/Singapore Dollar"),
                            ("USDHKD", "US Dollar/Hong Kong Dollar"),
                            ("USDTRY", "US Dollar/Turkish Lira"),
                            ("USDMXN", "US Dollar/Mexican Peso"),
                            ("USDZAR", "US Dollar/South African Rand"),
                            ("USDSEK", "US Dollar/Swedish Krona"),
                            ("USDDKK", "US Dollar/Danish Krone"),
                            ("USDNOK", "US Dollar/Norwegian Krone"),
                            ("USDINR", "US Dollar/Indian Rupee"),
                            ("USDTHB", "US Dollar/Thai Baht"),
                            ("EURCHF", "Euro/Swiss Franc"),
                            ("EURCAD", "Euro/Canadian Dollar"),
                            ("EURNZD", "Euro/New Zealand Dollar"),
                            ("GBPCHF", "British Pound/Swiss Franc"),
                            ("CADJPY", "Canadian Dollar/Japanese Yen"),
                            ("NZDCAD", "New Zealand Dollar/Canadian Dollar"),
                            ("XAUUSD", "Gold/US Dollar"),
                            ("XAGUSD", "Silver/US Dollar"),
                            ("XPTUSD", "Platinum/US Dollar"),
                            ("XPDUSD", "Palladium/US Dollar"),
                        ],
                        max_length=100,
                        verbose_name="Trading Pair",
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="signals_auth.mt5account",
                    ),
                ),
            ],
        ),
    ]
