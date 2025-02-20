import pandas as pd
import numpy as np

def get_sigs(env, data, df_price_his):
    sorted_data = dict(sorted(data.items()))
    sigs = []
    MOV = env['MOV']

    for date_str, value in sorted_data.items():
        current_index = df_price_his.index[df_price_his["Date"] == date_str].tolist()[0]
        price_t_1 = df_price_his.iloc[current_index - 1]    # t-1 個交易日的價格

        sig = 0
        if price_t_1["Close"] > price_t_1[MOV]:
            sig = 1
        elif price_t_1["Close"] < price_t_1[MOV]:
            sig = -1

        sigs.append([date_str, sig])

    return sigs


def overnight_rtn_list(env, sigs, df_price_his):
    '''
        long-term investment evaluation
    '''
    rtn_list = []   # daily return list
    in_out_list_sig = []
    position = 0
    enter_price = 0
    MOV = env['MOV']
    
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
                in_out_list_sig.append([date_str, "close", sig])
            elif position == -1:
                # Close
                rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                in_out_list_sig.append([date_str, "close", sig])
            elif position == 0:
                rtn = 0
            rtn_list.append([date_str, rtn])
            
            # print(rtn_list)
            # print(in_out_list_sig)
            
            return rtn_list, in_out_list_sig
        
        # print(sig, df_price.iloc[0]["Close"], df_price.iloc[0]["MA5"])
        open_price = df_price.iloc[0]["Open"]
        close_price = df_price.iloc[0]["Close"]
        if sig == 1:
            if position == 0:
                # long
                in_out_list_sig.append([date_str, "enter", sig])
                enter_price = open_price
                rtn = (close_price - enter_price) / enter_price
                enter_price = close_price
                position = 1
            elif position == 1:
                # hold
                rtn = (close_price - enter_price) / enter_price
                enter_price = close_price
            elif position == -1:
                # Close 
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (enter_price - open_price) / enter_price
                enter_price = 0
                position = 0
                
        elif sig == -1:        
            if position == 0:
                # Short
                in_out_list_sig.append([date_str, "enter", sig])
                enter_price = open_price
                rtn = (enter_price - close_price) / enter_price
                enter_price = close_price
                position = -1
            elif position == 1:
                # Close
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (open_price - enter_price) / enter_price
                enter_price = 0
                position = 0
            elif position == -1:
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

def eval_onlymov(env, data, df_price_his):
    '''
        Overnight Trade Eval : Evaluate Overnight return based on the individual
    '''
    # print(individual, end=" ")
    MOV = env['MOV']
    sigs = get_sigs(env, data, df_price_his)
    gain = []
    loss = []
    gain_precision = []
    loss_precision = []
    accumulated_rtn_list, in_out_sig_list = overnight_rtn_list(env, sigs, df_price_his)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    # print(in_out_sig_list)
    
    longshort = 'none'
    enter_price = 0
    for i, (date_str, state, sig) in enumerate(in_out_sig_list):

        if state == "enter":
            if sig == 1:
                longshort = 'long'
            elif sig == -1:
                longshort = 'short'
            enter_price = df_price_his[df_price_his["Date"] == pd.to_datetime(date_str, format="%Y%m%d")].iloc[0]["Open"]
            # print(f"enter  {longshort} \t {date_str} {enter_price}", end="\t")    
            
        close_price = df_price_his[df_price_his["Date"] == pd.to_datetime(date_str, format="%Y%m%d")].iloc[0]["Close"]
        if state == "close":
            if longshort == 'long':
                # print(f"close {date_str} {close_price}")
                rtn = (close_price - enter_price) / enter_price
                if rtn > 0:
                    tp += 1
                    gain.append(rtn)
                    gain_precision.append(rtn)
                else:
                    fp += 1
                    loss.append(rtn)
                    loss_precision.append(rtn)
            elif longshort == 'short':
                # print(f"close {date_str} {close_price}")
                rtn = (enter_price - close_price) / enter_price
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
