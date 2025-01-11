import json
import os
import re
import shutil
import numpy as np
import pandas as pd
from openai import OpenAI
from sklearn.cluster import KMeans
from datetime import datetime

from factor import StockFactor
from api import genetic_algorithm_accu
from api import eval_accu

class EvalAccumulated(StockFactor):
    '''
        Implement from StockFactor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env):
        # 初始化 OpenAI API
        self.client = OpenAI()
        self.client.api_key = os.getenv('OPENAI_API_KEY')
        self.env = env
        self.path_folder = "out_stock/OverNight_"
        self.path_out = self.path_folder + env['start_date'] + "_" + env['end_date'] + "/" + env['stock_id'] + "/"
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.path_embeddings = self.path_out + "embeddings.json"  # 輸出 JSON 檔案
        self.path_clustered_summaries = self.path_out + "clustered_summaries.json"  # 輸出 JSON 檔案
        self.path_factors = f"{self.path_out}/factors.json"
        self.path_expand = f"{self.path_out}/expand.json"
        self.price_his = self.get_price_his()
        
        self.similarity_threshold = 0.8  # 語意相似度閾值
        

    def run_taining(self, mode, train_datarange, test_datarange, re_run=False):
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
        best_individual = genetic_algorithm_accu(factors, state_file, file_gen, train_datarange, self.price_his, population_size=20, generations=50, mode=mode)
        # print(f"Best individual: {best_individual}")

        individual = best_individual
        res_train = eval_accu(individual, train_datarange, self.price_his)
        res_test = eval_accu(individual, test_datarange, self.price_his)
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