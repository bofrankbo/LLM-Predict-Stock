import json
import os
import re
import shutil
import numpy as np
import pandas as pd
from openai import OpenAI
from sklearn.cluster import KMeans
from datetime import datetime

from factor import Factor
from api import genetic_algorithm_on
from api import eval_on

class FactorON(Factor):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env, count=1):
        
        # data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.price_his = self.get_price_his()
        
        # output path
        self.env = env
        self.path_folder = "FactorON"
        self.run_count = count
        self.similarity_threshold = 0.8
        self.get_path()
        

    def run_taining(self, mode, train_datarange, test_datarange, re_run=False):
        env = self.env
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        state_file = out_folder + '/state.json'
        file_gen = out_folder + '/generation_results.json'
        file_result = out_folder + '/result.json'
        best_individual = genetic_algorithm_on(factors, state_file, file_gen, train_datarange, self.price_his, population_size=20, generations=50, mode=mode)


        individual = best_individual
        res_train = eval_on(individual, train_datarange, self.price_his)
        res_test = eval_on(individual, test_datarange, self.price_his)
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