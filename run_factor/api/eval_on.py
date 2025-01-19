import pandas as pd
import numpy as np
from collections import Counter

def get_sigs(data, individual, diff=0):
    sorted_data = dict(sorted(data.items()))
    sigs = []
    for date_str, value in sorted_data.items():
        daily_sigs = []

        # remove elements with sig = 0
        # Count the frequency of each element
        # Get the maximum frequency
        # If there is a tie, set sig to 0; otherwise, set it to the most frequent element
        sig = 0
        for i in range(len(individual)):
            if individual[i] == 1:
                daily_sigs.append(value["skeleton"][f"{str(i+1)}"]["sig"])

        if len(daily_sigs) > 0:
            count = Counter(daily_sigs)
            # print(count[1], count[-1])
            if count[1] > count[-1] + diff:
                sig = 1
            elif count[1] < count[-1] - diff:
                sig = -1

        sigs.append([date_str, sig])

    return sigs

def overnight_rtn_list(sigs, df_price_his):
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
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
            elif position == -1:
                # Close
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
            elif position == 0:
                rtn = 0
            rtn_list.append([date_str, rtn])

            return rtn_list, in_out_list_sig
        
        # print(sig, df_price.iloc[0]["Close"], df_price.iloc[0]["MA5"])
        if sig == 1 and df_price.iloc[0]["Close"]:
            if position == 0:
                # long
                in_out_list_sig.append([date_str, "enter", sig])
                enter_price = float(df_price.iloc[0]["Open"])
                rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
                position = 1
            elif position == 1:
                # hold
                rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
            elif position == -1:
                # Close 
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (enter_price - float(df_price.iloc[0]["Open"])) / enter_price
                enter_price = 0
                position = 0
                
        elif sig == -1 and df_price.iloc[0]["Close"]:        
            if position == 0:
                # Short
                in_out_list_sig.append([date_str, "enter", sig])
                enter_price = float(df_price.iloc[0]["Open"])
                rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
                position = -1
            elif position == 1:
                # Close
                in_out_list_sig.append([date_str, "close", sig])
                rtn = (float(df_price.iloc[0]["Open"]) - enter_price) / enter_price
                enter_price = 0
                position = 0
            elif position == -1:
                # hold
                rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
                
        else:
            if position == 0:
                # do nothing
                rtn = 0
            elif position == 1:
                # hold
                rtn = (float(df_price.iloc[0]["Close"]) - enter_price) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
            elif position == -1:
                # hold
                rtn = (enter_price - float(df_price.iloc[0]["Close"])) / enter_price
                enter_price = float(df_price.iloc[0]["Close"])
        rtn_list.append([date_str, rtn])
    

def eval_on(individual, data, df_price_his):
    '''
        Overnight Trade Eval : Evaluate Overnight return based on the individual
    '''
    # print(individual, end=" ")
    sigs = get_sigs(data, individual)
    gain = []
    loss = []
    gain_precision = []
    loss_precision = []
    accumulated_rtn_list, in_out_sig_list = overnight_rtn_list(sigs, df_price_his)
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
            
        if state == "close":
            if longshort == 'long':
                rtn = (df_price_his[df_price_his["Date"] == pd.to_datetime(date_str, format="%Y%m%d")].iloc[0]["Close"] - enter_price) / enter_price
                if rtn > 0:
                    tp += 1
                    gain.append(rtn)
                    gain_precision.append(rtn)
                else:
                    fp += 1
                    loss.append(rtn)
                    loss_precision.append(rtn)
            elif longshort == 'short':
                rtn = (enter_price - df_price_his[df_price_his["Date"] == pd.to_datetime(date_str, format="%Y%m%d")].iloc[0]["Close"]) / enter_price
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
