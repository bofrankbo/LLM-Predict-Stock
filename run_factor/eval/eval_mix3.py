import pandas as pd
import numpy as np
from collections import Counter
from eval.eval_daytrade import EvalDayTrade

class EvalMix3(EvalDayTrade):
    '''
        > EMA => BnH
        < EMA => DayTrade
    '''
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['MOV']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"

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
        

    def eval(self, sig_data, individual):
        '''
            Day Trade Eval : Evaluate daily return based on the individual
        '''
        # print(individual, end=" ")
        df_price_his = self.price_his
        sigs = self.get_sigs(sig_data, individual)
        gain = []
        loss = []
        gain_precision = []
        loss_precision = []
        accumulated_rtn_list, in_out_sig_list = self.trade_list(sigs, df_price_his)
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        # print(in_out_sig_list)
        
        
        longshort = 'none'
        enter_price = 0
        for i, (date_str, state, sig, price) in enumerate(in_out_sig_list):

            if state == "enter":
                if sig == 1:
                    longshort = 'long'
                elif sig == -1:
                    longshort = 'short'
                enter_price = price
                
            if state == "close":
                if longshort == 'long':
                    rtn = (price - enter_price) / enter_price
                    if rtn > 0:
                        tp += 1
                        gain.append(rtn)
                        gain_precision.append(rtn)
                    else:
                        fp += 1
                        loss.append(rtn)
                        loss_precision.append(rtn)
                elif longshort == 'short':
                    rtn = (enter_price - price) / enter_price
                    if rtn > 0: 
                        tn += 1
                        gain.append(rtn)    
                    else:
                        fn += 1
                        loss.append(rtn)
                # print(rtn)

        if tp + fp + tn + fn == 0 or tp + fp == 0 or tp + fn == 0:
            accuracy = precision = recall = ev = precision_ev = 0
        else:
            accuracy = (tp + tn) / (tp + fp + tn + fn)
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)

            if len(gain) == 0 or len(loss) == 0:
                ev = 0
            else:
                ev = np.mean(gain) * accuracy + np.mean(loss) * (1 - accuracy)

            if len(gain_precision) == 0 or len(loss_precision) == 0:
                precision_ev = 0
            else:
                precision_ev = np.mean(gain_precision) * precision + np.mean(
                    loss_precision
                ) * (1 - precision)

        result = {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "avail_count": tp + fp + tn + fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "ev": ev,
            "precision_ev": precision_ev,
            "rtn_list": accumulated_rtn_list,
        }
        # print()

        return result
