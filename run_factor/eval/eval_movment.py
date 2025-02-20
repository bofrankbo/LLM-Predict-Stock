import pandas as pd
import numpy as np
from collections import Counter
from eval.eval_overnight import EvalOvernight

class EvalMovment(EvalOvernight):
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['MOV']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"

    def trade_list(self, sigs, df_price_his):
        '''
            long-term investment evaluation
        '''
        rtn_list = []   # daily return list
        in_out_list_sig = []
        position = 0
        enter_price = 0
        MOV = self.env['MOV']
        
        for date_str, sig in sigs:

            date = pd.to_datetime(date_str, format="%Y%m%d")
            df_price = df_price_his[df_price_his["Date"] == date]

            current_index = df_price_his.index[df_price_his["Date"] == date].tolist()[0]
            price_t_1 = df_price_his.iloc[current_index - 1]    # t-1 個交易日的價格

            # print(df_price_yesterday)
            if df_price.empty:
                continue
            
            # print(date_str, sig, hold)
            # check is last day
            if date_str == sigs[-1][0]:
                # print("last day")
                if position == 1:
                    # Close
                    rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, float(df_price.iloc[0]["Close"])])
                elif position == -1:
                    # Close
                    rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, float(df_price.iloc[0]["Close"])])
                elif position == 0:
                    rtn = 0
                rtn_list.append([date_str, rtn])

                # print(in_out_list_sig)
                return rtn_list, in_out_list_sig
            
            # print(sig, df_price.iloc[0]["Close"], df_price.iloc[0]["MA5"])
            open_price = df_price.iloc[0]["Open"]
            close_price = df_price.iloc[0]["Close"]
            if sig == 1:
                if position == 0 and price_t_1["Close"] > price_t_1[MOV]:
                    # long
                    enter_price = open_price
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "enter", sig, enter_price])
                    enter_price = close_price
                    position = 1
                elif position == -1:
                    # Close 
                    rtn = (enter_price - open_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, open_price])
                    enter_price = 0
                    position = 0
                else:
                    if position == 0:
                        # hold
                        rtn = 0
                    else:
                        # hold
                        rtn = (close_price - enter_price) / enter_price
                        enter_price = close_price
                    
            elif sig == -1:        
                if position == 0 and price_t_1["Close"] < price_t_1[MOV]:
                    # Short
                    enter_price = open_price
                    rtn = (enter_price - close_price) / enter_price
                    in_out_list_sig.append([date_str, "enter", sig, enter_price])
                    enter_price = close_price
                    position = -1
                elif position == 1:
                    # Close
                    rtn = (open_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "close", sig, open_price])
                    enter_price = 0
                    position = 0
                else:
                    if position == 0:
                        # hold
                        rtn = 0
                    else:
                        # hold
                        rtn = (enter_price - close_price) / enter_price
                        enter_price = close_price
                    
            else:
                if position == 0:
                    # do nothing
                    rtn = 0
                elif position == 1:
                    # hold
                    rtn = (close_price  - enter_price) / enter_price
                    enter_price = close_price
                elif position == -1:
                    # hold
                    rtn = (enter_price - close_price) / enter_price
                    enter_price = close_price
            rtn_list.append([date_str, rtn])
