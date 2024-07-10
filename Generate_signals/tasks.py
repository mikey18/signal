from celery.signals import worker_ready
from celery import shared_task
from .TradeLogic.premium_tradelogic import Premium_Trade
from functions.CustomQuery import get_if_exists
import MetaTrader5 as mt5
import logging
import atexit
from Generate_signals.models import MT5Account, MT5Account_Symbols
logger = logging.getLogger(__name__)


def shutdown_mt5():
    mt5.shutdown()
    logging.info("MT5 shutdown successfully")
          

# @worker_ready.connect
# def start_mt5(**kwargs):
#     Premium_Trade().initiate_system()
 
@shared_task
def signal_trade_task(master_account, 
                      master_password, 
                      master_server, 
                      user_id, 
                      pair, 
                      group_name):
    classs = Premium_Trade()
    classs.initiate_system( 
        master_account=master_account,
        master_password=master_password,
        master_server=master_server, 
        user_id=user_id,              
        pair=pair,
        group_name=group_name
    )


@worker_ready.connect
def start_mt5(**kwargs):
    master_account = get_if_exists(MT5Account, master=True, verified=True)
    if not master_account:
        logger.error(f"No master account")
        return
    
    if not mt5.initialize():
    # if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        logger.error(f"MT5 initialization failed")
        raise RuntimeError("MT5 initialization failed")    
    logger.info(f"MT5 initialized successfully")
    login = mt5.login(login=master_account.account, 
                    password=master_account.password, 
                    server=master_account.server.name)
    if login:
        logger.info("Successfully logged in to demo account")
        account_symbols = MT5Account_Symbols.objects.filter(account=master_account, active=True)
    else:
        logger.error("Failed to login to demo account")
        return

    atexit.register(shutdown_mt5)
    for account_symbol in account_symbols:
        signal_trade_task.delay( 
            master_account=master_account.account,
            master_password=master_account.password,
            master_server=master_account.server.name, 
            user_id=master_account.user.id,              
            pair=account_symbol.pair,
            group_name=account_symbol.group_name
        )
        
    



