import json
import os
import re
import shutil
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from factor import Factor

class Movement(Factor):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env, count=1):

        self.env = env
        self.run_count = count
        self.path_folder = "Movement"
        self.get_path()
        
    def get_path(self):
        env = self.env
        # Data path of history data
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.price_his = self.get_price_his()
        
        # output path
        self.path_out =  f"{self.path_folder}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_embeddings = f"out_stock/Embeddings/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        self.path_clustered_summaries = f"out_stock/Cluster_summmaries/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        self.path_factors = f"out_stock/Factors/{self.path_out}/factors.json"    # 輸出 JSON 檔案
        self.path_expand = f"out_stock/Expands/{self.path_folder}/{env['stock_id']}/expand.json"    # 輸出 JSON 檔案
        self.training_path = f"out_stock/Training_result/{self.path_folder}/{env["MOV"]}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.similarity_threshold = 0.8    
    
    def get_result(self, mode=1):        
        with open(f"{self.training_path}/result.json", "r", encoding="utf-8") as f:
            res = json.load(f)
        
        return res
    
    def run_movment(self, eval_func):
        daterange = pd.date_range(self.env['start_date'], self.env['end_date'])
        
        start_day = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_day = datetime.strptime(self.env['end_date'], '%Y%m%d')

        # split to training and testing
        total_days = (end_day - start_day).days + 1
        split_point = int(total_days * 3 / 4)
        training_end_day = start_day + timedelta(days=split_point - 1)
        testing_start_day = training_end_day + timedelta(days=1)

        test_datarange = {}        
        for date in daterange:
            if testing_start_day <= date <= end_day:
                if not self.price_his[self.price_his["Date"] == date.strftime("%Y%m%d")].empty:
                    test_datarange[date.strftime("%Y%m%d")] = {"skeleton": ""}
        # print(data)
        res_test = eval_func(self.env, test_datarange, self.price_his)
        
        res = {
            "test": res_test,
        }
        # print(res)
        # print(file_result)
        self.env['path_result']  = self.training_path + '/result.json'
        os.makedirs(os.path.dirname(self.env['path_result']), exist_ok=True)
        with open(self.env['path_result'], 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
            
        df = pd.DataFrame([res['test']], index=['test'])

        return df