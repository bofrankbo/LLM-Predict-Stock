from api import eval
from api import genetic_algorithm
from api import factor_expanding2

import os
import re
import json
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from factor import StockFactor

class Factor2(StockFactor):
    def __init__(self, env):
        self.env = env
        self.path_folder = "out_stock/Factor2_"
        self.path_out = self.path_folder + env['start_date'] + "_" + env['end_date'] + "/" + env['stock_id'] + "/"
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.path_embeddings = self.path_out + "embeddings.json"  # 輸出 JSON 檔案
        self.path_clustered_summaries = self.path_out + "clustered_summaries.json"  # 輸出 JSON 檔案
        self.path_factors = f"{self.path_out}factors.json"
        self.path_expand = f"{self.path_out}expand.json"
        
        self.similarity_threshold = 0.8  # 語意相似度閾值
        
    def expand_factors(self, llm_factors):
        '''
            llm_factors: list of factors
            
            update factors.json
            it can generate new factors while old factors are not empty
            if old data is empty, then create a new one
        '''
        factors = {}
        
        if not os.path.exists(self.path_factors):
            print("No factors found, Please process Factors first")
            return

        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        # Access by index using list of keys
        key_list = list(factors.keys())
        value_list = list(factors.values())

        old_data = {}
        if os.path.exists(self.path_expand):
            with open(self.path_expand, "r", encoding="utf-8") as f:
                old_data = json.load(f)

        data = factor_expanding2(llm_factors, self.env, key_list, value_list, old_data)

        # 儲存資料
        with open(self.path_expand, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
