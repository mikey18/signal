from django.contrib import admin
from .models import (
    User,
    MT5Account,
    MT5Account_Symbols,
    Brokers,
    Devices,
    OneTimePassword,
    OldPassword,
)

admin.site.register(User)
admin.site.register(Devices)
admin.site.register(OneTimePassword)
admin.site.register(OldPassword)
admin.site.register(MT5Account)
admin.site.register(MT5Account_Symbols)
admin.site.register(Brokers)
