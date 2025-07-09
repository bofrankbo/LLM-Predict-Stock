import os
import json

from .expand_stock import Expanding
class UsableSoTExpanding(Expanding):
    def __init__(self, env, llm, price_his, expand=1):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_expand = f"{os.getcwd()}/backtest_llm_factor/out_stock/Expands/UsableSoT_{str(expand)}/{env['stock_id']}_expand.json" 
        
        if "components" in env:
            self.type = 'index'
            self.news_data = {}
            for stock in env["components"]:
                path_news_file = f"{os.getcwd()}/history_data/{stock[2]}/news_title/{stock[0]}news_title.json"
                with open(path_news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                self.news_data[stock[0]] = news_data
        else:
            self.type = 'stock'
            self.news_data = {}
            path_news_file = f"{os.getcwd()}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
            with open(path_news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            self.news_data[env['stock_id']] = news_data        
            
        # history data path
        self.path_news_file = f"{os.getcwd()}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"