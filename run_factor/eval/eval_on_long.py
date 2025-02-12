import pandas as pd
import numpy as np
from collections import Counter
from eval.eval_daytrade import EvalDayTrade

class EvalONLong(EvalDayTrade):
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        if 'fee' in env:
            self.fee = env['fee']
        else:
            self.fee = 0
        
    def overnight_rtn_list(self, sigs, df_price_his):
        '''
            long-term investment evaluation
        '''
        rtn_list = []   # daily return list
        in_out_list_sig = []
        position = 0
        enter_price = 0
        
        # print(sigs)
        
        for date_str, sig in sigs:

            date = pd.to_datetime(date_str, format="%Y%m%d")
            df_price = df_price_his[df_price_his["Date"] == date]

            # print(df_price)
            if df_price.empty:
                continue
            
            # print(date_str, sig, hold)
            # check is last day
            if date_str == sigs[-1][0]:
                # print("last day")
                if position == 1:
                    # Close
                    rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                    rtn = rtn - self.fee
                    in_out_list_sig.append([date_str, "close", sig, float(df_price.iloc[0]["Close"])])
                # elif position == -1:
                #     # Close
                #     rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                #     in_out_list_sig.append([date_str, "close", sig, float(df_price.iloc[0]["Close"])])
                elif position == 0:
                    rtn = 0
                rtn_list.append([date_str, rtn])

                # print(in_out_list_sig)
                return rtn_list, in_out_list_sig
            
            open_price = df_price.iloc[0]["Open"]
            close_price = df_price.iloc[0]["Close"]
            if sig == 1 and df_price.iloc[0]["Close"]:
                if position == 0:
                    # long
                    enter_price = open_price
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "enter", sig, enter_price])
                    enter_price = close_price
                    position = 1
                elif position == 1:
                    # hold
                    rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                    enter_price = float(df_price.iloc[0]["Close"])
                # elif position == -1:
                #     # Close 
                #     rtn = (enter_price - open_price) / enter_price
                #     in_out_list_sig.append([date_str, "close", sig, open_price])
                #     enter_price = 0
                #     position = 0
                    
            elif sig == -1 and df_price.iloc[0]["Close"]:        
                if position == 0:
                    # Short
                    # enter_price = open_price
                    rtn = 0
                    # in_out_list_sig.append([date_str, "enter", sig, enter_price])
                    enter_price = close_price
                    position = 0
                elif position == 1:
                    # Close
                    rtn = (open_price - enter_price) / enter_price
                    rtn = rtn - self.fee
                    in_out_list_sig.append([date_str, "close", sig, open_price])
                    enter_price = 0
                    position = 0
                # elif position == -1:
                #     # hold
                #     rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                #     enter_price = float(df_price.iloc[0]["Close"])
                    
            else:
                if position == 0:
                    # do nothing
                    rtn = 0
                elif position == 1:
                    # hold
                    rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                    enter_price = float(df_price.iloc[0]["Close"])
                # elif position == -1:
                #     # hold
                #     rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                #     enter_price = float(df_price.iloc[0]["Close"])
            rtn_list.append([date_str, rtn])
        

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
        accumulated_rtn_list, in_out_sig_list = self.overnight_rtn_list(sigs, df_price_his)
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
