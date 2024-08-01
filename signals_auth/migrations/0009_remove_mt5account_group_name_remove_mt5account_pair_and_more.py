# Generated by Django 5.0.6 on 2024-06-30 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals_auth", "0008_mt5account_symbols_group_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mt5account",
            name="group_name",
        ),
        migrations.RemoveField(
            model_name="mt5account",
            name="pair",
        ),
        migrations.AddField(
            model_name="mt5account_symbols",
            name="verified",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="mt5account_symbols",
            name="pair",
            field=models.CharField(
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
                    ("XAUAED", "Gold/United Arab Emirates Dirham"),
                    ("XAUARS", "Gold/Argentine Peso"),
                    ("XAUAUD", "Gold/Australian Dollar"),
                    ("XAUBRL", "Gold/Brazilian Real"),
                    ("XAUCAD", "Gold/Canadian Dollar"),
                    ("XAUCNY", "Gold/Chinese Yuan"),
                    ("XAUEUR", "Gold/Euro"),
                    ("XAUGBP", "Gold/British Pound"),
                    ("XAUHKD", "Gold/Hong Kong Dollar"),
                    ("XAUINR", "Gold/Indian Rupee"),
                    ("XAUJPY", "Gold/Japanese Yen"),
                    ("XAUMXN", "Gold/Mexican Peso"),
                    ("XAURUB", "Gold/Russian Ruble"),
                    ("XAUSAR", "Gold/Saudi Riyal"),
                    ("XAUTHB", "Gold/Thai Baht"),
                    ("XAUTRY", "Gold/Turkish New Lira"),
                    ("XAUTUSD", "Tether Gold - USD"),
                    ("XAGAED", "Silver/United Arab Emirates Dirham"),
                    ("XAGARS", "Silver/Argentine Peso"),
                    ("XAGAUD", "Silver/Australian Dollar"),
                    ("XAGBRL", "Silver/Brazilian Real"),
                    ("XAGCAD", "Silver/Canadian Dollar"),
                    ("XAGCNY", "Silver/Chinese Yuan"),
                    ("XAGEUR", "Silver/Euro"),
                    ("XAGGBP", "Silver/British Pound"),
                    ("XAGHKD", "Silver/Hong Kong Dollar"),
                    ("XAGINR", "Silver/Indian Rupee"),
                    ("XAGJPY", "Silver/Japanese Yen"),
                    ("XAGKRW", "Silver/Korean Won"),
                    ("XAGMXN", "Silver/Mexican Peso"),
                    ("XAGRUB", "Silver/Russian Ruble"),
                    ("XAGSAR", "Silver/Saudi Riyal"),
                    ("XAGTRY", "Silver/Turkish New Lira"),
                    ("XAGZAR", "Silver/South African Rand"),
                    ("^IXIC", "NASDAQ Composite Index"),
                    ("^NDX", "NASDAQ-100 Index"),
                    ("AAPL", "Apple Inc."),
                    ("MSFT", "Microsoft Corporation"),
                    ("AMZN", "Amazon.com Inc."),
                    ("GOOGL", "Alphabet Inc. (Class A)"),
                    ("FB", "Meta Platforms Inc. (formerly Facebook)"),
                    ("NVDA", "NVIDIA Corporation"),
                    ("TSLA", "Tesla Inc."),
                    ("PYPL", "PayPal Holdings Inc."),
                    ("INTC", "Intel Corporation"),
                    ("CSCO", "Cisco Systems Inc."),
                    ("AMD", "Advanced Micro Devices Inc."),
                    ("NFLX", "Netflix Inc."),
                    ("CMCSA", "Comcast Corporation"),
                    ("PEP", "PepsiCo Inc."),
                    ("SBUX", "Starbucks Corporation"),
                    ("ADBE", "Adobe Inc."),
                    ("QCOM", "Qualcomm Incorporated"),
                    ("BKNG", "Booking Holdings Inc."),
                ],
                max_length=100,
                verbose_name="Trading Pair",
            ),
        ),
    ]
