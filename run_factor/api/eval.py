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

def eval(individual, data, df_price_his):
    '''
        Day Trade Eval : Evaluate daily return based on the individual
    '''
    # print(individual, end=" ")
    sigs = get_sigs(data, individual)
    gain = []
    loss = []
    gain_precision = []
    loss_precision = []
    rtn_list = []
    # rtn_list = acumulate_calculate(sigs, df_price_his)
    ttl_count = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    i = 0
    for date_str, rtn in rtn_list:
        sig = sigs[i]
        i += 1
        
        # print(rtn)
        ttl_count += 1
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
            precision_ev = np.mean(gain_precision) * precision + np.mean(
                loss_precision
            ) * (1 - precision)

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
