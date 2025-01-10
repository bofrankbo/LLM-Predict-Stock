import pandas as pd
import numpy as np
import os
from collections import Counter

def eval(individual, data, df_price_his):
    # print(individual, end=" ")

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


    sorted_data = dict(sorted(data.items()))

    for date_str, value in sorted_data.items():
        ttl_count += 1
        sigs = []
        sig = 0
        for i in range(len(individual)):
            if individual[i] == 1:
                sigs.append(value["skeleton"][f"{str(i+1)}"]["sig"])

        # remove elements with sig = 0
        # Count the frequency of each element
        # Get the maximum frequency
        # If there is a tie, set sig to 0; otherwise, set it to the most frequent element
        # sigs = list(filter(lambda a: a != 0, sigs))
        if len(sigs) > 0:

            count = Counter(sigs)

            # print(count[1], count[-1])
            diff = 0
            if count[1] > count[-1] + diff:
                sig = 1
            elif count[1] < count[-1] - diff:
                sig = -1

        # print(date_str, sigs, sig, end=" ")

        df_price = df_price_his[
            df_price_his["Date"] == pd.to_datetime(date_str, format="%Y%m%d")
        ]

        if df_price.empty:
            continue
        
        close = float(df_price.iloc[0]["Close"])
        open = float(df_price.iloc[0]["Open"])
        rtn = (close - open) / open

        if pd.isna(rtn):
            rtn = 0
        # print(rtn)
        if sig == 1:
            # print("sig > 0",rtn)
            rtn_list.append([date_str, rtn])
            if rtn > 0:
                tp += 1
                gain.append(rtn)
                gain_precision.append(rtn)
            else:
                fp += 1
                loss.append(rtn)
                loss_precision.append(rtn)
        elif sig == -1:
            # print("sig < 0",rtn)
            rtn_list.append([date_str, -rtn])
            if rtn < 0:
                tn += 1
                gain.append(-rtn)
            else:
                fn += 1
                loss.append(-rtn)
        else:
            rtn_list.append([date_str, 0])

    accuracy = 0
    precision = 0
    recall = 0
    ev = 0


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
            precision_ev = np.mean(gain_precision) * precision + np.mean(loss_precision) * (1 - precision)

    result = {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "avail_count": tp + fp + tn + fn,
        "ttl_count": ttl_count,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "ev": ev,
        "precision_ev": precision_ev,
        "rtn_list": rtn_list,
    }
    # print()

    return result
