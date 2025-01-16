from api import eval
from api import genetic_algorithm
from api import factor_expanding
from api import split_expand

import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from factor import Factor


class Test1(Factor):
    def __init__(self, env):
        self.env = env
        self.path_folder = "out_stock/GA_factor_"
        self.path_out = self.path_folder + env['start_date'] + "_" + env['end_date'] + "/" + env['stock_id'] + "/"
        self.path_factors = f"{self.path_out}/factors.json"
        self.path_expand = f"{self.path_out}/expand.json"
        self.price_his = self.get_price_his()
        
    

    def run_taining(self, mode, train_datarange, test_datarange, individual, re_run=False):
        env = self.env
        if mode == 0:
            out_folder = f"{self.path_out}ac"
        elif mode == 1:
            out_folder = f"{self.path_out}ev"
        
        if re_run:
            if os.path.isdir(out_folder):
                shutil.rmtree(out_folder)
            elif os.path.isfile(out_folder):
                os.remove(out_folder)
            
        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        state_file = out_folder + '/state.json'
        file_gen = out_folder + '/generation_results.json'
        file_result = out_folder + '/result.json'

        # print("Start, 第一次跑的話請確認state是空的")
        # best_individual = genetic_algorithm(factors, state_file, file_gen, train_datarange, self.price_his, population_size=20, generations=50, mode=mode)
        # print(f"Best individual: {best_individual}")

        res_train = eval(individual, train_datarange, self.price_his)
        res_test = eval(individual, test_datarange, self.price_his)
        res = {
            "train": res_train,
            "test": res_test,
            "individual": individual,
        }
        # print(res)
        # print(file_result)
        with open(file_result, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)

        # print(res['test'])
        df = pd.DataFrame([res['train'], res['test']], index=['train', 'test'])

        return df