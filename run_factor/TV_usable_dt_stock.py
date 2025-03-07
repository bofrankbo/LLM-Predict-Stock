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
from langchain_openai import OpenAIEmbeddings

from eval import EvalDayTrade
from module import GeneticAlgorithm
from module import UsableGenerator
from module import UsableExpanding
from factor import Factor

class TV_UsableFactorDT(Factor):
    def __init__(self, env):
        self.env = env
        self.run_count = env['run_count']
        self.path_folder = "UsableDT"
        self.env['path_folder'] = self.path_folder
        
        # output path
        self.training_path = f"out_stock/Training_result_TV/{self.path_folder}/{str(self.run_count)}/TV{env['tv']}/{env['stock_id']}"
        self.env['training_path'] = self.training_path
        
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
        fac_exp = UsableExpanding(self.env, self.llm, self.price_his)
        self.factors = fac_gen.generate_factors()
        self.exp_data = fac_exp.expanding(self.factors)
        self.eval_module = EvalDayTrade(self.env, self.price_his)
        
    def get_price_his(self):
        country = self.env['country']
        stock_id = self.env['stock_id']
        path_price_his = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{country}/stock_price/{stock_id}tech.csv"
        # print(path_price_his)
        df_price_his = pd.read_csv(path_price_his, encoding="utf-8")
        df_price_his["Date"] = pd.to_datetime(df_price_his["Date"], format="%Y%m%d")
        return df_price_his

    def get_individual(self, mode):
        env = self.env
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        with open(f"{out_folder}/result.json", "r", encoding="utf-8") as f:
            res = json.load(f)
            individual = res['individual']
        print(individual, "individual")
        return individual

    def training(self, mode, train_datarange, test_datarange):
        res = self.eval_module.get_result(mode)
        if res == None:
            ga = GeneticAlgorithm(self.env, self.price_his, train_datarange, self.eval_module.eval, pop_size=20, generations=50, mode=mode, pop_len=len(self.factors.keys()))
            individual = ga.run()
            
            res_train = self.eval_module.eval(train_datarange, individual)
            res_test = self.eval_module.eval(test_datarange, individual)
            res = {
                "train": res_train,
                "test": res_test,
                "individual": individual,
            }
            self.eval_module.save_result(res, mode)
    
    def split_exp(self, tv=15):
        start_day = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_day = datetime.strptime(self.env['end_date'], '%Y%m%d')

        data_points = self.exp_data

        # split to training and testing
        total_days = (end_day - start_day).days + 1
        split_point = int(total_days * tv / 31)
        training_end_day = start_day + timedelta(days=split_point - 1)
        testing_start_day = training_end_day + timedelta(days=1)
        train_datarange = {}
        for date_str, value in data_points["output_data"].items():
            date = datetime.strptime(date_str, '%Y%m%d')
            if start_day <= date <= training_end_day:
                train_datarange[date_str] = value
        test_datarange = {}
        for date_str, value in data_points["output_data"].items():
            date = datetime.strptime(date_str, '%Y%m%d')
            if testing_start_day <= date <= end_day:
                test_datarange[date_str] = value

        return train_datarange, test_datarange
    
    def get_result(self, mode):
        eval_module = EvalDayTrade(self.env, self.price_his)
        res = eval_module.get_result(mode)
        return res
    
    def get_return_list(self, type='test'):
        eval_module = EvalDayTrade(self.env, self.price_his)
        result = eval_module.get_result(1)
        res_test = result[type]
        df_price_his = self.price_his
        price_dict = df_price_his.set_index(df_price_his['Date'].dt.strftime('%Y%m%d'))['Close'].to_dict()

        list_date = []
        list_bnh_rtn = []
        list_stag_rtn = []
    
        for date, rtn in res_test['rtn_list']:
            list_date.append(date)
            list_bnh_rtn.append(price_dict.get(date, None))  # 若 date 不存在，回傳 None 避免錯誤
            list_stag_rtn.append(rtn)
            
        return list_date, list_bnh_rtn, list_stag_rtn
    
    def show_sig(self):
        fac_exp = UsableExpanding(self.env, self.llm, self.price_his)
        fac_exp.show_sig()
        
    def show_individual(self, mode):
        individuals = self.get_individual(mode)
        
        fac_gen = UsableGenerator(self.env, self.price_his)
        factors = fac_gen.generate_factors()
        
        i = 0
        for key, value in factors.items():
            if individuals[i] == 1:
                print(key, value)
            i += 1
        print("")