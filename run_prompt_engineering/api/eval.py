import pandas as pd
import json
import os
from collections import Counter

def eval(individual, data, env):
    country = env['country']
    stock_id = env['stock_id']

    gain = []
    loss = []
    gain_precision = []
    loss_precision = []
    rtn_list = []
    ttl_count = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    path_price_his = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{country}/stock_price/{stock_id}.csv"
    df_price_his = pd.read_csv(path_price_his, encoding='utf-8')
    df_price_his['Date'] = pd.to_datetime(df_price_his['Date'], format='%Y%m%d')
    sorted_data = dict(sorted(data.items()))

    for date_str, value in sorted_data.items():
        ttl_count += 1
        # print(date_str, value)
        
        sigs = []
        sig = 0
        for i in range(len(individual)):

            if individual[i] == 1:
                sigs.append(value['skeleton'][f'{str(i+1)}']['sig'])
            
        # remove elements with sig = 0
        sigs = list(filter(lambda a: a != 0, sigs))

        if len(sigs) > 0:
            # Count the frequency of each element
            # Get the maximum frequency
            # If there is a tie, set sig to 0; otherwise, set it to the most frequent element
            count = Counter(sigs)
            max_count = max(count.values())
            most_frequent = [k for k, v in count.items() if v == max_count]

            if len(most_frequent) > 1:
                sig = 0
            else:
                sig = most_frequent[0]

        df_price = df_price_his[df_price_his['Date'] == pd.to_datetime(date_str, format='%Y%m%d')]

        if df_price.empty:
            continue

        rtn = (float(df_price.iloc[0]['Close']) - float(df_price.iloc[0]['Open']))  / float(df_price.iloc[0]['Open']) 
        if pd.isna(rtn):
            rtn = 0

        

        if sig > 0:
            rtn_list.append([date_str,rtn])
            if rtn > 0:
                tp += 1
                gain.append(rtn)
                gain_precision.append(rtn)
            else:
                fp += 1
                loss.append(rtn)
                loss_precision.append(rtn)
        elif sig == -1:
            rtn_list.append([date_str,-rtn])
            if rtn < 0:
                tn += 1
                gain.append(-rtn)
            else:
                fn += 1
                loss.append(-rtn)
        else:
            rtn_list.append([date_str,rtn])

    accuracy = 0
    precision = 0
    recall = 0
    ev = 0
    if tp + fp + tn + fn == 0 or tp + fp == 0 or tp + fn == 0:
        accuracy = 0
        precision = 0
        recall = 0
        ev = 0
        precision_ev = 0
    elif len(gain) == 0 or len(loss) == 0:
        accuracy = (tp + tn) / (tp + fp + tn + fn)
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        ev = 0
        if len(gain_precision) == 0 or len(loss_precision) == 0:
            precision_ev = 0
        else:
            precision_ev = (sum(gain_precision) / len(gain_precision))*precision + (sum(loss_precision) / len(loss_precision))*(1-precision)

    else:
        accuracy = (tp + tn) / (tp + fp + tn + fn)
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        ev = (sum(gain) / len(gain))*accuracy + (sum(loss) / len(loss))*(1-accuracy)
        if len(gain_precision) == 0 or len(loss_precision) == 0:
            precision_ev = 0
        else:
            precision_ev = (sum(gain_precision) / len(gain_precision))*precision + (sum(loss_precision) / len(loss_precision))*(1-precision)

    result = {
        'tp' : tp,
        'fp' : fp,
        'tn' : tn,
        'fn' : fn,
        'avail_count' : tp + fp + tn + fn,
        'ttl_count' : ttl_count,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'ev': ev,
        'precision_ev' : precision_ev,
        'rtn_list' : rtn_list
    }

    return result