import asyncio
from datetime import datetime, timezone, timedelta
import pandas as pd
import vectorbt as vbt
import MetaTrader5 as mt5
import logging
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from functions.notifications import send_notification_sync
from Generate_signals.models import Trade_History
from signals_auth.models import MT5Account
logger = logging.getLogger(__name__)

class Premium_Trade:
    def __init__(self):
        self.channel_layer = get_channel_layer()

    async def get_buy_or_sell_signal(self):
        try:
            # while True:
            bars = mt5.copy_rates_from(self.symbol, mt5.TIMEFRAME_M1, datetime.now(timezone.utc), 365)
            df = pd.DataFrame(bars)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df = df.set_index("time")
            current_price = df["close"].iloc[-1]

            # Calculate indicators
            # logger.info("Calculating indicators in progress...")
            ma14 = vbt.MA.run(df["close"], 14)
            ma50 = vbt.MA.run(df["close"], 50)
            ma365 = vbt.MA.run(df["close"], 365)
            rsi = vbt.RSI.run(df["close"], 14)
            
            # Check the conditions for the last bar
            # logger.info("Checking conditions in progress...\n")
            if (not (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40)
            and not (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59)):
                logger.info(f"checking for signal, account - {mt5.account_info().name}, pair - {self.symbol}")

                data = {
                    "status": False,
                    "message": "checking for signal...",
                    "data": {
                        "symbol": self.symbol,
                    }
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        **data
                    }
                )
                return data

            elif (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40):
                logger.info("buy signal found")

                data = {
                    "status": True,
                    "condition":"BUY",
                    "RSI":rsi.rsi.iloc[-1],
                    "14 SMA": ma14.ma.iloc[-1],
                    "Current Price": current_price,
                    
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": True,
                        "message":"BUY",
                        "data": {
                            "symbol": self.symbol,
                        }
                    }
                )
                return data
            
            elif (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59):
                logger.info("sell signal found")

                data = {
                    "status": True,
                    "condition":"SELL",
                    "RSI":rsi.rsi.iloc[-1],
                    "14 SMA": ma14.ma.iloc[-1],
                    "Current Price": current_price
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": True,
                        "message":"SELL",
                        "data": {
                            "symbol": self.symbol,
                        }
                    }
                )             
                return data
            # await asyncio.sleep(59)  # wait for 59 seconds
        except Exception as e:
            logger.error(f"Error in WebSocket task: {e}")

    async def check_profit_or_loss(self, initial_balance):
        # Get the new balance from the MT5 terminal
        account_info = mt5.account_info()
        new_balance = account_info.balance

        if initial_balance < new_balance:
            return "profit"
        elif initial_balance > new_balance:
            return "loss"
        else:
            return "no change"

    async def check_open_positions(self):
        open_positions = mt5.positions_get()
        symbol_positions = [position for position in open_positions if position.symbol == self.symbol]
        
        for position in symbol_positions:
            if position.comment.lower().startswith("signal"):
                self.open_position = position
                return True
        return False
    
    async def check_trade_history(self):
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        deals = mt5.history_deals_get(start_time, end_time)

        if deals is None:
            return False
        
        self.last_closed_trade = None
        for deal in reversed(deals):
            if deal.symbol == self.symbol and deal.comment.lower().startswith("signal"):
                self.last_closed_trade = deal
                return True
        return False

    async def wait_for_trade_close(self, order_id):
        while True:
            # Get all active orders
            if not await self.check_open_positions():
                return True
            
            logger.info(f"automated trade in progress 2 - {self.symbol}")
            await self.channel_layer.group_send(
                self.room,
                {
                    "type": "trade.format",
                    "status": True,
                    "message": "active trade in progress",
                    "data": {
                        "symbol": self.open_position.symbol,
                        "trade_type": "BUY" if self.open_position.type == 0 else "SELL",
                        "stop_loss": self.open_position.sl,
                        "take_profit": self.open_position.tp,
                        "open_price": self.open_position.price_open,
                        "curent_price": self.open_position.price_current
                    }
                }
            )
            await asyncio.sleep(1)  # wait for a second before checking again

    async def place_trade(self, symbol, volume, sl, tp, trade_type, price):
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "sl": sl,
                "tp": tp,
                "price": price,
                # "price": await self.get_price(symbol, trade_type),
                "deviation": 200,
                "magic": 123456,
                "type": mt5.ORDER_TYPE_BUY if trade_type == "BUY" else mt5.ORDER_TYPE_SELL,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "comment": f"signal.{self.current_phase}.{self.current_step}"
            }
            result = mt5.order_send(request)        
            return result
        except Exception as e:
            logger.error(f"place trade error: {e}")

    async def login_and_place_trade_slave(self, user, symbol, trade_type, price):
        # logger.info(f"sl = {sl} tp = {tp}")
        account = await database_sync_to_async(MT5Account.objects.get)(user=user)
        login = await self.login_to_mt5(account.account,
                                        account.password,
                                        account.server)
        
        if login:
            sl, tp, lot_size = await self.get_sl_tp_lot_size(trade_type, price)
            while True:
                result = await self.place_trade(symbol, lot_size, sl, tp, trade_type, price)
                logger.info(result)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    logger.info("trade error")
                else:
                    logger.info(f"trade placed for user id - {user.id}, name {user.fullname}")
                    break # Exit the loop if the trade is successful

    async def place_trade_slave_accounts(self, symbol, trade_type, price, master_result):
        accounts = await database_sync_to_async(list)(MT5Account.objects.filter(verified=True, master=False))
        for account in accounts:
            user = await database_sync_to_async(lambda: account.user)()
            await self.login_and_place_trade_slave(user, symbol, trade_type, price)
            send_notification_sync.delay(
                user_id=user.id,
                title="Trade placed",
                body=f"Signal was received and trade has been placed - {self.symbol}"
            )

        await self.login_to_mt5(
            self.master_account,
            self.master_password,
            self.master_server
        )
        closed_trade = await self.wait_for_trade_close(master_result.order)
        if closed_trade:
            trade_status = await self.check_profit_or_loss(self.initial_balance)
            return {"status": "success", "order": master_result.order, "retcode": master_result.retcode, "trade_status": trade_status}

    async def place_buy_or_sell_trade(self, data):
        if await self.check_open_positions():
            return {"status": "error", "message": "There is already an open trade"}

        symbol = data["symbol"]
        volume = data["volume"]
        sl = data["sl"]
        tp = data["tp"]
        condition = data["condition"]
        price=data["price"]

        # while True:
        logger.info(f"Placing trade - {symbol}")
        master_result = await self.place_trade(symbol, volume, sl, tp, condition, price)
        logger.info(master_result)
        if master_result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.info(f"trade couldn't place - {symbol} | comment - {master_result.comment} | reetcode - {master_result.retcode}")
            # if master_result.retcode == mt5.TRADE_RETCODE_TRADE_DISABLED or master_result.retcode == mt5.TRADE_RETCODE_PRICE_OFF:
            return {"status": "error", "retcode": master_result.retcode, "message": master_result.comment}
            # else:
            #     continue
        else:
            logger.info(f"trade placed - {symbol}")
            # THIS IS ON HOLD
            # slave_accounts_trade = await self.place_trade_slave_accounts(symbol, condition, price, master_result)
            # THIS IS ON HOLD
            # # send notification
            send_notification_sync.delay(
                user_id=self.user_id,
                title="Trade placed",
                body=f"Signal was received and trade has been placed - {self.symbol}"
            )
            # send notification
            
            await self.channel_layer.group_send(
                self.room,
                {
                    "type": "trade.format",
                    "status": True,
                    "message": "Signal was received and trade has been placed",
                    "data": {
                        "symbol": self.symbol,
                    }
                }
            )
            closed_trade = await self.wait_for_trade_close(master_result.order)
            if closed_trade:
                trade_status = await self.check_profit_or_loss(self.initial_balance)
                return {"status": "success", "order": master_result.order, "retcode": master_result.retcode, "trade_status": trade_status}

                # THIS IS ON HOLD
                # if slave_accounts_trade["status"] == "success":
                #     return {
                #         "status": "success", 
                #         "order": slave_accounts_trade["order"], 
                #         "retcode": slave_accounts_trade["retcode"], 
                #         "trade_status": slave_accounts_trade["trade_status"]
                #     }

    async def get_price(self, symbol, trade_type):
        tick_info = mt5.symbol_info_tick(symbol)
        price = tick_info.ask if trade_type == "BUY" else tick_info.bid
        return price

    async def convert_pips_to_price(self, price, pips, point):
        return price + (pips * point)
    
    async def calculate_initial_lot_size(self, balance):
        risk = 0.001 
        stop_loss_pips = 250  
        self.initial_balance = balance
        money_to_risk = self.initial_balance * risk

        if type(money_to_risk) is int:
            initial_lot_size = round((money_to_risk / stop_loss_pips), 1)
            return initial_lot_size
        elif type(money_to_risk) is float:
            calculation = money_to_risk / stop_loss_pips
            if calculation < 0.01:
                initial_lot_size = 0.01
                return initial_lot_size
            else:
                initial_lot_size = await self.convert_to_two_decimal_places(calculation)
                return initial_lot_size
    
    async def PHASES_DATA(self):
        initial_lot_size = await self.calculate_initial_lot_size(mt5.account_info().balance)
        logger.info(initial_lot_size)
        phases = {
            phase: [(phase * initial_lot_size, 250, 750), 
                    (phase * initial_lot_size, 250, 750), 
                    (phase * initial_lot_size, 500, 1500), 
                    (phase * initial_lot_size, 1000, 3000)]
            for phase in range(1, 13)
        }
        return phases

    async def get_sl_tp_lot_size(self, condition, price):
        # Get the lot size, stop loss, and take profit for the current phase and step
        phases = await self.PHASES_DATA()
        lot_size, stop_loss_pips, take_profit_pips = phases[self.current_phase + 1][self.current_step]            

        # Get the current price
        point = mt5.symbol_info(self.symbol).point
        
        # Calculate the stop loss and take profit prices
        multiplier = 1 if condition == "BUY" else -1
        stop_loss = await self.convert_pips_to_price(price, multiplier * -stop_loss_pips, point)
        take_profit = await self.convert_pips_to_price(price, multiplier * take_profit_pips, point)

        return stop_loss, take_profit, lot_size
    
    async def convert_to_two_decimal_places(self, value):
        async def has_more_than_two_decimal_places(value):
            # Convert the value to a string to check the number of decimal places
            str_value = str(value)
            
            # Check if the value has a decimal point
            if "." in str_value:
                # Split the string into the integer and decimal parts
                parts = str_value.split(".")
                # Check if the decimal part has more than two digits
                return len(parts[1]) > 2
            return False
        
        if await has_more_than_two_decimal_places(value):
            # Use round() to round the value to two decimal places
            value = round(value, 2)
        return value
    
    async def save_to_db(self, symbol, stop_loss, take_profit, open_price, trade_type, initial_balance):
        account = await database_sync_to_async(MT5Account.objects.get)(user__id=self.user_id)
        await database_sync_to_async(Trade_History.objects.create)(
            account=account,
            symbol=symbol,
            stop_loss=stop_loss,
            take_profit=take_profit,
            price=open_price,
            type=trade_type,
            result=initial_balance
        )

    async def adjust_phases_and_steps(self, trade_status):
        if trade_status == "loss":
            if self.current_step < 3:
                self.current_step += 1
            else:
                new_balance = mt5.account_info().balance

                if self.current_phase < 11:
                    self.phase_initial_balances[self.current_phase + 1] = new_balance
                    self.current_phase += 1
                else:
                    self.phase_initial_balances = {}
                    self.current_phase = 0
                self.current_step = 0

        elif trade_status == "profit":            
            if self.current_phase > 0:
                new_balance = mt5.account_info().balance
                # previous_initial_balance = self.phase_initial_balances[(self.current_phase + 1) - 1]
                # if previous_initial_balance:
                
                for phase, value in self.phase_initial_balances.items():
                    if new_balance > value:
                        self.current_phase = phase
                        self.current_step = 0
                        break
                    else:
                        self.current_step = 0
                # if new_balance > previous_initial_balance:
                #     self.current_phase -= 1
                #     self.current_step = 0
                # else:
                #     self.current_step = 0
                # else:
                #     self.current_step = 0
            else:
                self.current_step = 0
    
    async def shutdown_mt5():
        mt5.shutdown()
        logging.info("MT5 shutdown successfully") 
    
    async def login_to_mt5(self, account, password, server):
        login = mt5.login(login=account, 
                            password=password, 
                            server=server)
        return login

    async def money_management(self, **kwargs):
        logger.info(f"id {kwargs.get('user_id')}")
        self.user_id = kwargs.get("user_id")
        self.master_account = kwargs.get("master_account")
        self.master_password = kwargs.get("master_password")
        self.master_server = kwargs.get("master_server")
        self.symbol = kwargs.get("pair")
        self.room = kwargs.get("group_name")     
        self.initial_balance = mt5.account_info().balance      
        self.phase_initial_balances = {}
        self.current_phase = 0
        self.current_step = 0
        trade_was_active = False
        trade_data = None
        self.open_position = False
        
        while True:
            if await self.check_open_positions():
                trade_was_active = True
                logger.info(f"automated trade in progress 1 - {self.symbol}")
                trade_data = {
                    "symbol": self.open_position.symbol,
                    "trade_type": "BUY" if self.open_position.type == 0 else "SELL",
                    "stop_loss": self.open_position.sl,
                    "take_profit": self.open_position.tp,
                    "open_price": self.open_position.price_open,
                    "lot_size": self.open_position.volume
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": True,
                        "message": "active trade in progress",
                        "data": {
                            **trade_data,
                            "curent_price": self.open_position.price_current
                        }
                    }
                )
                await asyncio.sleep(1)
                continue
            
            # Checks if active trade was from signal server
            if trade_was_active:
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": True,
                        "message": "Trade completed",
                        "data": {
                            "symbol": self.open_position.symbol,
                            "result": await self.check_profit_or_loss(self.initial_balance),  # trade_status will be either "profit" or "loss"
                            "trade_type": trade_data["trade_type"],
                            "current_phase": self.current_phase + 1, # int
                            "current_step": self.current_step, # int
                            "lot_size": trade_data["lot_size"], # float
                            "stop_loss": trade_data["stop_loss"], # float
                            "take_profit": trade_data["take_profit"], # float
                            "new_account_balance": mt5.account_info().balance # float
                        }
                    }
                )
                # Save trade to db
                logger.info(f"saving to db 1 - {self.symbol}")
                trade_status = await self.check_profit_or_loss(self.initial_balance)
                await self.save_to_db(trade_data["symbol"], 
                                        trade_data["stop_loss"],
                                        trade_data["take_profit"],
                                        trade_data["open_price"],
                                        trade_data["trade_type"],
                                        trade_status)
             

                parts = self.open_position.comment.lower().split(".")
                logger.info(f"{parts} - {self.symbol}")
                self.current_phase = int(parts[1])
                self.current_step = int(parts[2])

                self.open_position = False
                trade_was_active = False
                trade_data = None

                # adjust phases and steps
                await self.adjust_phases_and_steps(trade_status)
                print(self.phase_initial_balances)
            # else:
            #     last_closed = await self.check_trade_history()
            #     if last_closed:
            #         print('last closed')
            #         parts = self.last_closed_trade.comment.lower().split(".")
            #         logger.info(f"{parts} - {self.symbol}")
            #         logger.info(f"{parts} - {self.symbol}")
            #         self.current_phase = int(parts[1])
            #         self.current_step = int(parts[2])
            #         await self.adjust_phases_and_steps(trade_status)
            # Checks if active trade was from signal server
            # Call the signal API
            signal_response = await self.get_buy_or_sell_signal()
            # signal_response = {"status": True, "condition":"BUY"}

            # If the signal is not "buy" or "sell", skip this iteration
            if signal_response["status"] is False:
                await asyncio.sleep(59)
                continue
         
            # Get the lot size, stop loss, and take profit for the current phase and step
            # Get the current price
            price = await self.get_price(self.symbol, signal_response["condition"])
            
            # Calculate the stop loss and take profit prices
            sl, tp, lot_size = await self.get_sl_tp_lot_size(signal_response["condition"], price)
            logger.info(f"price - {price} | sl - {sl} | tp - {tp} | lot size - {lot_size}")

            # Define the trade request
            trade_request = {
                "symbol": self.symbol,
                "volume": lot_size,
                "sl": sl,
                "tp": tp,
                "condition": signal_response["condition"],
                "price": price
            }

            # Send the trade request to the appropriate API and get the trade result
            if signal_response["condition"] == "BUY" or signal_response["condition"] == "SELL":
                response = await self.place_buy_or_sell_trade(trade_request)

            # Check the response
            if response["status"] == "success":
                # Save trade to db
                logger.info(f"saving to db 2 - {self.symbol}")
                await self.save_to_db(self.symbol, 
                                        sl,
                                        tp,
                                        price,
                                        signal_response["condition"],
                                        response["trade_status"])

                # adjust phases and steps
                parts = self.open_position.comment.lower().split(".")
                logger.info(f"{parts} - {self.symbol}")
                self.current_phase = int(parts[1])
                self.current_step = int(parts[2])
                await self.adjust_phases_and_steps(response["trade_status"])
                print(self.phase_initial_balances)

                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": True,
                        "message": "Trade completed",
                        "data": {
                            "symbol": self.symbol,
                            "result": response["trade_status"],  # trade_status will be either "profit" or "loss"
                            "trade_type": signal_response["condition"],
                            "current_phase": self.current_phase + 1, # int
                            "current_step": self.current_step, # int
                            "lot_size": lot_size, # float
                            "stop_loss": sl, # float
                            "take_profit": tp, # float
                            "new_account_balance": mt5.account_info().balance # float
                        }
                    }
                )
            else:
                # logger.info(f"trade couldn't place - {response['message']}")
                await self.channel_layer.group_send(
                    self.room,
                    {
                        "type": "trade.format",
                        "status": False,
                        "message": f"Trade request failed - {self.symbol} - {response['message']}",
                        "data": {
                            "symbol": self.symbol,
                        }
                    }
                )
            await asyncio.sleep(59)

    def initiate_system(self, **kwargs):
        asyncio.run(self.money_management(**kwargs))