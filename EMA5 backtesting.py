from colorama import Fore, Back, Style
from colorama import init
import pandas as pd
import datetime
import talib
import pdb
from pprint import pprint

init()
# watchlist = ['ACC', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'AMBUJACEM', 'APOLLOHOSP', 'ASIANPAINT', 'AUROPHARMA',
#              'AXISBANK', 'BAJAJ-AUTO', 'BAJAJFINSV', 'BAJAJHLDNG', 'BAJFINANCE', 'BANDHANBNK', 'BANKBARODA',
#              'BERGEPAINT', 'BHARTIARTL', 'BIOCON', 'BOSCHLTD', 'BPCL', 'BRITANNIA', 'CHOLAFIN', 'CIPLA', 'COALINDIA',
#              'COLPAL', 'DABUR', 'DIVISLAB', 'DLF', 'DMART', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GLAND', 'GODREJCP',
#              'GRASIM', 'HAVELLS', 'HCLTECH', 'HDFC', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO',
#              'HINDPETRO', 'HINDUNILVR', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IGL', 'INDIGO', 'INDUSINDBK',
#              'INDUSTOWER', 'INFY', 'IOC', 'ITC', 'JINDALSTEL', 'JSWSTEEL', 'JUBLFOOD', 'KOTAKBANK', 'LT', 'LTI',
#              'LUPIN', 'MARICO', 'MARUTI', 'MCDOWELL-N', 'MUTHOOTFIN', 'M&M', 'NAUKRI', 'NESTLEIND', 'NIFTY 50',
#              'NIFTY BANK', 'NMDC', 'NTPC', 'ONGC', 'PEL', 'PGHH', 'PIDILITIND', 'PIIND', 'PNB', 'POWERGRID', 'RELIANCE',
#              'SAIL', 'SBICARD', 'SBILIFE', 'SBIN', 'SHREECEM', 'SIEMENS', 'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS',
#              'TATASTEEL', 'TCS', 'TECHM', 'TITAN', 'TORNTPHARM', 'ULTRACEMCO', 'UPL', 'VEDL', 'WIPRO', 'YESBANK']

watchlist = ['SBIN']

risk_capacity = 10000
indicator = "ema"
ema_period = 5
timeframe = '5minutes'
tgt_multiplier = 3

status = {'signal_candle': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None, 'entry_price': 0,
          'qty': None, 'sl': None, 'tg': None, 'exit_time': None, 'exit_price': None, 'pnl': None, 'traded': None,
          'remark': None, 'reentry_flag': None}
final_result = {}
tradeno = 0

for name in watchlist:
    print(name)
    df = pd.read_csv('D:\\algo\data\\stockdata\\Extrect Files\\5 minute\\SBIN.csv')
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    df['5ema'] = talib.EMA(df['close'], timeperiod=ema_period)
    df['trigger_candle_date'] = df['date'].shift(1)
    df = df.set_index(df['date'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[75:]

    for dtime, candle in df.iterrows():

        time_before_10_am = datetime.time(9, 15) < candle['date'].time() < datetime.time(10, 00)
        no_previos_trade = status['traded'] is None
        if time_before_10_am:
            try:
                trigger_candle = df.loc[candle['trigger_candle_date']]
            except Exception as e:
                continue

            # entry signal has came
            buy_signal_1 = trigger_candle['low'] > trigger_candle['5ema']
            buy_signal_2 = candle['low'] < trigger_candle['low']
            no_previos_trade = status['traded'] is None
            reentry = (status['reentry_flag'] is None)

            if buy_signal_1 and buy_signal_2 and no_previos_trade and reentry:
                # print(f"{Fore.YELLOW} entry for {name} on {dtime} {Fore.WHITE}")
                print(f"entry for {name} on {dtime}")
                st_date = str(dtime)[:10] + " 09:15:00+05:30"
                ed_date = str(dtime)[:10] + " " + str(dtime)[11:]
                temp_df = df[st_date:ed_date]
                SL = temp_df['high'].max()
                try:
                    status['qty'] = int(risk_capacity / (SL - trigger_candle['low']))
                    if status['qty'] <= 0:
                        print(f"trade not taken for {name} as SL value exceeds risk capacity")
                        continue
                except Exception as e:
                    print(f"trade not taken for {name} as SL, entry values are not valid")
                    continue
                tradeno = tradeno + 1
                status['name'] = name
                status['signal_candle'] = str(trigger_candle['date'])[11:19]
                status['date'] = str(dtime)[:10]
                status['buysell'] = "sell"
                status['entry_price'] = trigger_candle['low']
                status['entry_time'] = str(dtime)[11:19]
                status['sl'] = SL
                sl_points = status['sl'] - status['entry_price']
                status['tg'] = status['entry_price'] - (tgt_multiplier * sl_points)
                status['traded'] = "yes"
                continue

        if time_before_10_am and no_previos_trade and (status['reentry_flag'] == 1):
            try:
                trigger_candle = df.loc[candle['trigger_candle_date']]
                buy_signal_1 = trigger_candle['low'] > trigger_candle['5ema']
                buy_signal_2 = candle['low'] < trigger_candle['low']
                no_previos_trade = status['traded'] is None
                reentry = (status['reentry_flag'] == 1)
            except Exception as e:
                print(e)
                pdb.set_trace()

            if buy_signal_1 and buy_signal_2 and no_previos_trade and reentry:
                # print(f"{Fore.YELLOW} entry for {name} on {dtime} {Fore.WHITE}")
                print(f"reentry for {name} on {dtime}")
                st_date = str(dtime)[:10] + " 09:15:00+05:30"
                ed_date = str(dtime)[:10] + " " + str(dtime)[11:]
                temp_df = df[st_date:ed_date]
                SL = temp_df['high'].max()
                try:
                    status['qty'] = int(risk_capacity / (SL - trigger_candle['low']))
                    if status['qty'] <= 0:
                        print(f"reentry trade not taken for {name} as SL value exceeds risk capacity")
                        continue
                except Exception as e:
                    print(f"trade not taken for {name} as SL, entry values are not valid")
                    continue
                tradeno = tradeno + 1
                status['name'] = name
                status['signal_candle'] = str(trigger_candle['date'])[11:19]
                status['date'] = str(dtime)[:10]
                status['buysell'] = "sell"
                status['entry_price'] = trigger_candle['low']
                status['entry_time'] = str(dtime)[11:19]
                status['sl'] = SL
                sl_points = status['sl'] - status['entry_price']
                status['tg'] = status['entry_price'] - (tgt_multiplier * sl_points)
                status['traded'] = "yes"
                continue

        if (status['traded'] == 'yes'):

            # if sl_hit or target_hit or market_over:
            sl_hit = candle['high'] > status['sl']
            target_hit = candle['low'] <= status['tg']
            market_over = candle['date'].time() > datetime.time(15, 15)

            if sl_hit or target_hit or market_over:
                if sl_hit:
                    # print(f"{Fore.RED} SL hit for {name} on {dtime} {Fore.WHITE}")
                    print(f"SL hit for {name} on {dtime}")
                    pnl = (status['entry_price'] - status['sl']) * status['qty']
                    status['exit_price'] = status['sl']
                    status['pnl'] = pnl
                    status['remark'] = "SL hit"

                if target_hit:
                    # print(f"{Fore.GREEN} TGT hit for {name} on {dtime} {Fore.WHITE}")
                    print(f"TGT hit for {name} on {dtime}")
                    pnl = (status['entry_price'] - status['tg']) * status['qty']
                    status['exit_price'] = status['tg']
                    status['pnl'] = pnl
                    status['remark'] = "TGT hit"

                if market_over:
                    # print(f"{Fore.GREEN} market over for {name} on {dtime} {Fore.WHITE}")
                    print(f"market over for {name} on {dtime}")
                    pnl = (status['entry_price'] - candle['close']) * status['qty']
                    status['exit_price'] = candle['close']
                    status['pnl'] = pnl
                    status['remark'] = "market over"

                status['exit_time'] = str(candle['date'].time())
                final_result[tradeno] = status
                if status['reentry_flag'] == 1:
                    status = {'signal_candle': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None,
                              'entry_price': 0, 'qty': None, 'sl': None, 'tg': None, 'exit_time': None,
                              'exit_price': None, 'pnl': None, 'traded': None, 'remark': None, 'reentry_flag': 2}
                if status['reentry_flag'] is None:
                    status = {'signal_candle': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None,
                              'entry_price': 0, 'qty': None, 'sl': None, 'tg': None, 'exit_time': None,
                              'exit_price': None, 'pnl': None, 'traded': None, 'remark': None, 'reentry_flag': 1}

        market_over = candle['date'].time() > datetime.time(15, 15)
        no_trades_taken = status['traded'] is None

        if market_over and no_trades_taken:
            status = {'signal_candle': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None,
                      'entry_price': 0, 'qty': None, 'sl': None, 'tg': None, 'exit_time': None, 'exit_price': None,
                      'pnl': None, 'traded': None, 'remark': None, 'reentry_flag': None}

res = pd.DataFrame(final_result).T
res = res[['name', 'date', 'signal_candle', 'entry_time', 'buysell', 'entry_price', 'qty', 'sl', 'tg', 'exit_time',
           'exit_price', 'pnl', 'remark']]
res.to_excel('Backtesting SBIN 5 EMA result.xlsx')
