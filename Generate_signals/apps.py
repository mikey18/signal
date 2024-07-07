from django.apps import AppConfig
# from .TradeLogic.initializeMT5 import start_mt5
import MetaTrader5 as mt5

class GenerateSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Generate_signals'

    # def ready(self):
    #     # Initialize connection to MetaTrader 5 platform
    #     if not mt5.initialize():
    #         print("initialize() failed, error code =", mt5.last_error())
    #         quit()

    #     # # Fetch all symbols using wildcard filter
    #     # symbols = mt5.symbols_get("*")

    #     # # Check for errors
    #     # if not symbols:
    #     #     print("Failed to get symbols:", mt5.last_error())
    #     # else:
    #     #     # Iterate through the list of symbols
    #     #     for symbol_info in symbols:
    #     #         print(symbol_info.name)  # Print the symbol name

    #     # Shutdown connection to MetaTrader 5 platform
    #     mt5.shutdown()
