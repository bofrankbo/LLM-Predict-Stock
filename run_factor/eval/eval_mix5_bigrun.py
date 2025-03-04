import pandas as pd
import numpy as np
from collections import Counter
from eval.eval_overnight import EvalOvernight

class EvalBigRunMix5(EvalOvernight):
    '''
        pre 60 days EMA > 60 => BnH
        pre 60 days EMA < 60 => DayTrade
    '''
    def __init__(self, env, price_his):
        self.env = env
        price_his["Date"] = pd.to_datetime(price_his["Date"], format="%Y%m%d")
        price_his.set_index("Date", inplace=True)
        price_his.sort_index(inplace=True)
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"

    def trade_list(self, sigs, df_price_his, MOV, date_len):
        '''
            Short-term intraday trading below 60-day EMA, long-term holding above
        '''
        rtn_list = []  # daily return list
        in_out_list_sig = []
        position = 0
        enter_price = 0

        for date_str, sig in sigs:
            date = pd.to_datetime(date_str, format="%Y%m%d")
            df_price = df_price_his.loc[[date]]
            if df_price.empty:
                continue
            
            # get the previous 60 days price data
            pre_datelen_price = df_price_his.loc[df_price_his.index < date].tail(date_len)
            upperthenema = (pre_datelen_price["Close"] > pre_datelen_price[MOV]).sum()

            open_price = df_price.iloc[0]["Open"]
            close_price = df_price.iloc[0]["Close"]

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
            if upperthenema < date_len/2:  #  pre 60 days EMA < 60, seem as bear, intraday trade
                # print(f"{MOV} has only less then half of {date_len} days higher then ema seem as bear, do DayTrade")
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
            else:  # pre 60 days EMA > 60, seem as bull, buy and hold
                # print(f"{MOV} has more then half of {date_len} days higher then ema seem as bull, do BnH")
                if position == 0:
                    enter_price = open_price
                    position = 1
                    rtn = (close_price - enter_price) / enter_price
                    in_out_list_sig.append([date_str, "enter", 1, enter_price]) # seem as long sig set to 1
                    enter_price = close_price
                elif position == 1:
                    position = 1
                    rtn = (close_price - enter_price) / enter_price
                    enter_price = close_price
                              
            rtn_list.append([date_str, rtn])

        return rtn_list, in_out_list_sig
    
    def binary_to_decimal(self, individual):
        last_16_bits = individual[-16:]  # 取得最後16個數字
        # 分成兩個8位元
        mov_8 = last_16_bits[:8]
        date_len_8 = last_16_bits[8:]
        binary_str = ''.join(map(str, mov_8))  # 轉換成字串
        binary_str2 = ''.join(map(str, date_len_8))  # 轉換成字串
        decimal_value = int(binary_str, 2)  # 轉換成十進位
        decimal_value2 = int(binary_str2, 2)  # 轉換成十進位
        return str(decimal_value + 1), decimal_value2 + 1
    
    def eval(self, sig_data, individual):
        '''
            Evaluate the performance of the individual
        '''
        # print(individual, end=" ")
        mov_day, date_len = self.binary_to_decimal(individual)
        mov = 'EMA' + mov_day
        df_price_his = self.price_his
        sigs = self.get_sigs(sig_data, individual)
        gain = []
        loss = []
        gain_precision = []
        loss_precision = []
        accumulated_rtn_list, in_out_sig_list = self.trade_list(sigs, df_price_his, mov, date_len)
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        # print(in_out_sig_list)
        
        
        longshort = 'none'
        enter_price = 0
        for i, (date_str, state, sig, price) in enumerate(in_out_sig_list):
            # print(date_str, state, sig, price)
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

        if tp + fp + tn + fn == 0:
            accuracy = precision = recall = ev = precision_ev = 0            
        else:
            accuracy = (tp + tn) / (tp + fp + tn + fn)
            if tp + fp == 0:
                precision = 0
            else:
                precision = tp / (tp + fp)
            if tp + fn == 0:
                recall = 0
            else:
                recall = tp / (tp + fn)

            if len(gain) == 0 or len(loss) == 0:
                if len(gain) == 0 and len(loss) == 0:
                    ev = 0
                elif len(gain) == 0:
                    ev = np.mean(loss)
                elif len(loss) == 0:
                    ev = np.mean(gain)
            else:
                ev = np.mean(gain) * accuracy + np.mean(loss) * (1 - accuracy)

            if len(gain_precision) == 0 or len(loss_precision) == 0:
                precision_ev = 0
            else:
                precision_ev = np.mean(gain_precision) * precision + np.mean(loss_precision) * (1 - precision)

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