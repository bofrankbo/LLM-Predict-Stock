import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI

from eval import EvalDayTrade
from eval import EvalONLong
from module import GeneticAlgorithm
from module import UsableGenerator
from module import Index_UsableExpanding
from usable_mix_index import Index_UsableFactorMix
from factor import Factor

class Index_UsableFactorMix_Statictic(Index_UsableFactorMix):
    def __init__(self, env):
        self.env = env
        self.run_count = env['run_count']
        self.path_folder = "FactorUsableMix_statictic_DT"
        self.env['path_folder'] = self.path_folder
        self.do_ON = False
        
        # output path
        self.training_path = f"out_stock/Training_result/{self.path_folder}/{str(self.run_count)}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.similarity_threshold = 0.8
        
        # get history data
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.price_his = self.get_price_his()
        
        # models
        self.llm = ChatOpenAI(
            openai_api_key = os.getenv('OPENAI_API_KEY'),
            model='gpt-4o-mini',
            temperature=1,
        )
        
    def run(self):
        # preprocess
        fac_gen = UsableGenerator(self.env, self.price_his)
        fac_exp = Index_UsableExpanding(self.env, self.llm, self.price_his)
        self.factors = fac_gen.generate_factors()
        self.exp_data = fac_exp.expanding(self.factors)
        
        train_datarange, test_datarange = self.split_exp()
        # 計算前一季的數據範圍
        n = len(train_datarange) // 3  # 取整數部分

        sorted_date = list(test_datarange.keys())[-n:]
        upperthenema = 0
        mask = self.price_his['Date'].apply(lambda d: d.strftime("%Y%m%d") in sorted_date)
        dates = self.price_his.loc[mask]
        for index, row in dates.iterrows():
            if float(row['Close']) > float(row['EMA60']):
                upperthenema += 1
        
        self.eval_module = EvalDayTrade(self.env, self.price_his)     
        # self.eval_module = EvalONLong(self.env, self.price_his)        
           
        # if upperthenema > len(dates)/2:
        #     print("多頭做過夜")
        #     self.eval_module = EvalONLong(self.env, self.price_his)
        # else:
        #     print("空頭做當沖")
        #     self.eval_module = EvalDayTrade(self.env, self.price_his)
        

    def training(self, mode, train_datarange, test_datarange):
        # ga = GeneticAlgorithm(self.env, self.price_his, train_datarange, self.eval_module.eval, pop_size=20, generations=50, mode=mode, pop_len=len(self.factors.keys()))
        # 生成和 self.factors 一樣長度的 individual
        individual = [1] * len(self.factors.keys())
        
        res_train = self.eval_module.eval(train_datarange, individual)
        res_test = self.eval_module.eval(test_datarange, individual)
        res = {
            "train": res_train,
            "test": res_test,
            "individual": individual,
        }
        self.eval_module.save_result(res, mode)

        return res