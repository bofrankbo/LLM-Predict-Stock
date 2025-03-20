import os
from module.expand_stock import Expanding
class UsableExpanding(Expanding):
    def __init__(self, env, llm, price_his, expand=1):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_expand = f"out_stock/Expands/Usable_{str(expand)}/{env['stock_id']}_expand.json" 
        
        if "components" in env:
            self.type = 'index'
        else:
            self.type = 'stock'
            
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"