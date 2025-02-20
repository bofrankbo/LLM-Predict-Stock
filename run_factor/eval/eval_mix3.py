import pandas as pd
import numpy as np
from collections import Counter
from eval.eval_overnight import EvalOvernight

class EvalMix3(EvalOvernight):
    '''
        > EMA => BnH
        < EMA => DayTrade
    '''
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"

    def trade_list(self, sigs, df_price_his):
        '''
            Short-term intraday trading below 60-day EMA, long-term holding above
        '''
        rtn_list = []  # daily return list
        in_out_list_sig = []
        position = 0
        enter_price = 0
        MOV = self.env['MOV']

        for date_str, sig in sigs:
            date = pd.to_datetime(date_str, format="%Y%m%d")
            df_price = df_price_his[df_price_his["Date"] == date] # Price data for the day

            if df_price.empty:
                continue
            
            current_index = df_price_his.index[df_price_his["Date"] == date].tolist()[0]
            price_t_1 = df_price_his.iloc[current_index - 1]  # Previous day's price data

            open_price = df_price.iloc[0]["Open"]
            close_price = df_price.iloc[0]["Close"]
            ema_60 = df_price.iloc[0][MOV]

            # Last trading day handling
            if date_str == sigs[-1][0]:
                if position == 1:
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, close_price])
                elif position == -1:
                    rtn = (enter_price - close_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, close_price])
                else:
                    rtn = 0
                rtn_list.append([date_str, rtn])
                return rtn_list, in_out_list_sig

            # Trading logic
            if price_t_1["Close"] < price_t_1[MOV]:  # Below EMA 60, intraday trade
                if position == 0:
                    if sig == 1:    # long
                        enter_price = open_price
                        rtn = (close_price - enter_price) / enter_price
                        in_out_list_sig.append([date_str, "enter", sig, enter_price])
                        in_out_list_sig.append([date_str, "close", sig, close_price])
                        position = 0  # Reset position
                    elif sig == -1:   # short
                        enter_price = open_price
                        rtn = (enter_price - close_price) / enter_price
                        in_out_list_sig.append([date_str, "enter", sig, enter_price])
                        in_out_list_sig.append([date_str, "close", sig, close_price])
                        position = 0  # Reset position
                    elif sig == 0:   # do nothing
                        rtn = 0
                elif position == 1:     # Close buy and hold position
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, open_price])
                    position = 0
            else:  # Above EMA 60, buy and hold
                if position == 0:
                    enter_price = open_price
                    position = 1
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "enter", sig, enter_price])
                    enter_price = close_price
                elif position == 1:
                    position = 1
                    rtn = (close_price - enter_price) / enter_price
                    enter_price = close_price
                              
            rtn_list.append([date_str, rtn])

        return rtn_list, in_out_list_sig
