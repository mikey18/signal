from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import random
import string


class TradingPair(models.TextChoices):
    # Major Currency Pairs
    EUR_USD = "EURUSD", "Euro/US Dollar"
    USD_JPY = "USDJPY", "US Dollar/Japanese Yen"
    GBP_USD = "GBPUSD", "British Pound/US Dollar"
    # GBP_EUR = 'GBPEUR', 'British Pound/Euro',
    USD_CHF = "USDCHF", "US Dollar/Swiss Franc"
    USD_CAD = "USDCAD", "US Dollar/Canadian Dollar"
    AUD_USD = "AUDUSD", "Australian Dollar/US Dollar"
    NZD_USD = "NZDUSD", "New Zealand Dollar/US Dollar"

    # Minor Currency Pairs
    EUR_GBP = "EURGBP", "Euro/British Pound"
    EUR_JPY = "EURJPY", "Euro/Japanese Yen"
    GBP_JPY = "GBPJPY", "British Pound/Japanese Yen"
    AUD_JPY = "AUDJPY", "Australian Dollar/Japanese Yen"
    NZD_JPY = "NZDJPY", "New Zealand Dollar/Japanese Yen"
    AUD_NZD = "AUDNZD", "Australian Dollar/New Zealand Dollar"
    AUD_CAD = "AUDCAD", "Australian Dollar/Canadian Dollar"
    GBP_AUD = "GBPAUD", "British Pound/Australian Dollar"
    GBP_CAD = "GBPCAD", "British Pound/Canadian Dollar"
    EUR_AUD = "EURAUD", "Euro/Australian Dollar"

    # Exotic Currency Pairs
    USD_SGD = "USDSGD", "US Dollar/Singapore Dollar"
    USD_HKD = "USDHKD", "US Dollar/Hong Kong Dollar"
    USD_TRY = "USDTRY", "US Dollar/Turkish Lira"
    USD_MXN = "USDMXN", "US Dollar/Mexican Peso"
    USD_ZAR = "USDZAR", "US Dollar/South African Rand"
    USD_SEK = "USDSEK", "US Dollar/Swedish Krona"
    USD_DKK = "USDDKK", "US Dollar/Danish Krone"
    USD_NOK = "USDNOK", "US Dollar/Norwegian Krone"
    USD_INR = "USDINR", "US Dollar/Indian Rupee"
    USD_THB = "USDTHB", "US Dollar/Thai Baht"

    # Regional Currency Pairs
    EUR_CHF = "EURCHF", "Euro/Swiss Franc"
    EUR_CAD = "EURCAD", "Euro/Canadian Dollar"
    EUR_NZD = "EURNZD", "Euro/New Zealand Dollar"
    GBP_CHF = "GBPCHF", "British Pound/Swiss Franc"
    CAD_JPY = "CADJPY", "Canadian Dollar/Japanese Yen"
    NZD_CAD = "NZDCAD", "New Zealand Dollar/Canadian Dollar"

    # Precious Metals
    XAU_USD = "XAUUSD", "Gold/US Dollar"
    XAG_USD = "XAGUSD", "Silver/US Dollar"
    XPT_USD = "XPTUSD", "Platinum/US Dollar"
    XPD_USD = "XPDUSD", "Palladium/US Dollar"
    XAU_AED = "XAUAED", "Gold/United Arab Emirates Dirham"
    XAU_ARS = "XAUARS", "Gold/Argentine Peso"
    XAU_AUD = "XAUAUD", "Gold/Australian Dollar"
    XAU_BRL = "XAUBRL", "Gold/Brazilian Real"
    XAU_CAD = "XAUCAD", "Gold/Canadian Dollar"
    XAU_CNY = "XAUCNY", "Gold/Chinese Yuan"
    XAU_EUR = "XAUEUR", "Gold/Euro"
    XAU_GBP = "XAUGBP", "Gold/British Pound"
    XAU_HKD = "XAUHKD", "Gold/Hong Kong Dollar"
    XAU_INR = "XAUINR", "Gold/Indian Rupee"
    XAU_JPY = "XAUJPY", "Gold/Japanese Yen"
    XAU_MXN = "XAUMXN", "Gold/Mexican Peso"
    XAU_RUB = "XAURUB", "Gold/Russian Ruble"
    XAU_SAR = "XAUSAR", "Gold/Saudi Riyal"
    XAU_THB = "XAUTHB", "Gold/Thai Baht"
    XAU_TRY = "XAUTRY", "Gold/Turkish New Lira"
    XAU_USD_TETHER = "XAUTUSD", "Tether Gold - USD"
    XAG_AED = "XAGAED", "Silver/United Arab Emirates Dirham"
    XAG_ARS = "XAGARS", "Silver/Argentine Peso"
    XAG_AUD = "XAGAUD", "Silver/Australian Dollar"
    XAG_BRL = "XAGBRL", "Silver/Brazilian Real"
    XAG_CAD = "XAGCAD", "Silver/Canadian Dollar"
    XAG_CNY = "XAGCNY", "Silver/Chinese Yuan"
    XAG_EUR = "XAGEUR", "Silver/Euro"
    XAG_GBP = "XAGGBP", "Silver/British Pound"
    XAG_HKD = "XAGHKD", "Silver/Hong Kong Dollar"
    XAG_INR = "XAGINR", "Silver/Indian Rupee"
    XAG_JPY = "XAGJPY", "Silver/Japanese Yen"
    XAG_KRW = "XAGKRW", "Silver/Korean Won"
    XAG_MXN = "XAGMXN", "Silver/Mexican Peso"
    XAG_RUB = "XAGRUB", "Silver/Russian Ruble"
    XAG_SAR = "XAGSAR", "Silver/Saudi Riyal"
    XAG_TRY = "XAGTRY", "Silver/Turkish New Lira"
    XAG_ZAR = "XAGZAR", "Silver/South African Rand"

    # NASDAQ
    NASDAQ_COMPOSITE = "^IXIC", "NASDAQ Composite Index"
    NASDAQ_100 = "NAS100", "NASDAQ-100 Index"
    AAPL = "AAPL.US", "Apple Inc."
    MSFT = "MSFT", "Microsoft Corporation"
    AMZN = "AMZN.US", "Amazon.com Inc."
    GOOGL = "GOOGL", "Alphabet Inc. (Class A)"
    FB = "FB", "Meta Platforms Inc. (formerly Facebook)"
    NVDA = "NVDA", "NVIDIA Corporation"
    TSLA = "TSLA", "Tesla Inc."
    PYPL = "PYPL", "PayPal Holdings Inc."
    INTC = "INTC", "Intel Corporation"
    CSCO = "CSCO", "Cisco Systems Inc."
    AMD = "AMD", "Advanced Micro Devices Inc."
    NFLX = "NFLX", "Netflix Inc."
    CMCSA = "CMCSA", "Comcast Corporation"
    PEP = "PEP", "PepsiCo Inc."
    SBUX = "SBUX", "Starbucks Corporation"
    ADBE = "ADBE", "Adobe Inc."
    QCOM = "QCOM", "Qualcomm Incorporated"
    BKNG = "BKNG", "Booking Holdings Inc."

    # CRYPTO CURRENCY
    BTC_USD = "BTCUSD", "Bitcoin/US Dollar"
    ETH_USD = "ETHUSD", "Ethereum/US Dollar"


class TimeFrame(models.TextChoices):
    # TICK = 'tick', 'Tick'
    SECOND_1 = "1s", "1 Second"
    MINUTE_1 = "1m", "1 Minute"
    MINUTE_5 = "5m", "5 Minutes"
    MINUTE_15 = "15m", "15 Minutes"
    MINUTE_30 = "30m", "30 Minutes"
    HOUR_1 = "1h", "1 Hour"
    HOUR_4 = "4h", "4 Hours"
    DAY_1 = "1d", "1 Day"
    WEEK_1 = "1w", "1 Week"
    MONTH_1 = "1mo", "1 Month"


class TradingPairTypes(models.TextChoices):
    CURRENCY = "currency", "currency"
    STOCKS = "stocks", "stocks"
    CRYPTOCURRENCY = "cryptocurrency", "cryptocurrency"
    FUTURES = "futures", "futures"
    METALS = "metals", "metals"


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# class RefreshTokens(models.Model):
#     user = models.OneToOneField(User, on_delete=models.PROTECT, default=None)
#     token = models.CharField(max_length=5000)

#     def __str__(self):
#         return self.user.email


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, default=None)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return self.user.email


class OldPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=200)

    def __str__(self):
        return self.user.email


class Devices(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_agent = models.CharField(max_length=200)
    language = models.CharField(max_length=200)
    login_time = models.CharField(max_length=200, blank=True)
    logout_time = models.CharField(max_length=200, blank=True)
    logged_in = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Brokers(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=1000, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)


class MT5Account(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account = models.BigIntegerField()
    password = models.CharField(max_length=150)
    server = models.ForeignKey(Brokers, on_delete=models.CASCADE)
    activate_automation = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    master = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class MT5Account_Symbols(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(MT5Account, on_delete=models.CASCADE)
    pair = models.CharField(
        max_length=100,
        choices=TradingPair.choices,
        verbose_name="Trading Pair",
        blank=True,
    )
    type = models.CharField(
        max_length=100,
        choices=TradingPairTypes.choices,
        verbose_name="Trading Pair types",
        blank=True,
    )
    group_name = models.CharField(max_length=150, blank=True, null=True, unique=True)
    active = models.BooleanField(default=True)

    def generate_string(self):
        letters = string.ascii_letters  # Includes both uppercase and lowercase letters
        return "".join(random.choice(letters) for _ in range(8))

    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = self.generate_string()
            while MT5Account_Symbols.objects.filter(
                group_name=self.group_name
            ).exists():
                self.group_name = self.generate_string()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account.user.email} --- {self.active} --- {self.pair}"
