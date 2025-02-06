import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI

from usable_on import UsableFactorON

from module import GeneticAlgorithmVIX
from module import UsableGenerator
from module import UsableExpanding
from eval import EvalVolatility


class UsableVolatility(UsableFactorON):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env, count=1):        
        self.env = env
        self.run_count = env['run_count']
        self.path_folder = "UsableMOV"
        self.env['path_folder'] = self.path_folder
        
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
        fac_exp = UsableExpanding(self.env, self.llm, self.price_his)
        self.factors = fac_gen.generate_factors()
        self.exp_data = fac_exp.expanding(self.factors)
        
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
        
        return individual

    def training(self, mode, train_datarange, test_datarange):
        eval_module = EvalVolatility(self.env, self.price_his)
        ga = GeneticAlgorithmVIX(self.env, self.price_his, train_datarange, eval_module.eval, pop_size=20, generations=50, mode=mode, pop_len=len(self.factors.keys()))
        individual = ga.run()
        
        res_train = eval_module.eval(train_datarange, individual)
        res_test = eval_module.eval(test_datarange, individual)
        res = {
            "train": res_train,
            "test": res_test,
            "individual": individual,
        }
        eval_module.save_result(res, mode)

        return res
    
    def get_result(self, mode):
        eval_module = EvalVolatility(self.env, self.price_his)
        res = eval_module.get_result(mode)
        return res
    
    def get_return_list(self):
        eval_module = EvalVolatility(self.env, self.price_his)
        result = eval_module.get_result(1)
        res_test = result['test']
        df_price_his = self.price_his
        
        list_date = []
        list_bnh_rtn = []
        list_stag_rtn = []

        for date, rtn in res_test['rtn_list']:
            # print(rtn)
            list_date.append(date)
            list_bnh_rtn.append(df_price_his[df_price_his['Date'].dt.strftime('%Y%m%d') == date]['Close'].values[0])
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