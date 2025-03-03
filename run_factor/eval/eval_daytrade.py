import json
import pandas as pd
import numpy as np
import os
from collections import Counter


class EvalDayTrade:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his 
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        if 'fee' in env:
            self.fee = env['fee']
        else:
            self.fee = 0
            
    def get_eval_path(self):
        return self.training_path
    
    def get_result(self, mode):
        # print(self.training_path)
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        self.path_result = f"{out_folder}/result.json"
        if os.path.exists(self.path_result):
            with open(self.path_result, "r", encoding="utf-8") as f:
                res = json.load(f)
        else:
            res = None
        return res
    
    def save_result(self, res, mode):
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        os.makedirs(out_folder, exist_ok=True)
        with open(f"{out_folder}/result.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
            
    def load_result(self, mode):
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        if not os.path.exists(f"{out_folder}/result.json"):
            return None
        
        with open(f"{out_folder}/result.json", "r", encoding="utf-8") as f:
            res = json.load(f)
        
        return res

    def get_sigs(self, sig_data, individual):
        sorted_data = dict(sorted(sig_data.items()))
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
                    if str(i+1) in value["skeleton"]:
                        daily_sigs.append(value["skeleton"][f"{str(i+1)}"]["sig"])

                if len(daily_sigs) > 0:
                    count = Counter(daily_sigs)
                    # print(count[1], count[-1])
                    if count[1] > count[-1]:
                        sig = 1
                    elif count[1] < count[-1]:
                        sig = -1

            sigs.append([date_str, sig])
        return sigs

    def eval(self, sig_data, individual):
        '''
            Day Trade Eval : Evaluate daily return based on the individual
        '''
        
        # print(individual, end=" ")
        sigs = self.get_sigs(sig_data, individual)
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
        df_price_his = self.price_his
        
        for date_str, sig in sigs:
            
            open_price = df_price_his.loc[df_price_his["Date"] == date_str, "Open"].values[0]
            close_price = df_price_his.loc[df_price_his["Date"] == date_str, "Close"].values[0]
            
            rtn = (close_price - open_price) / open_price
            rtn = rtn - self.fee

            
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
