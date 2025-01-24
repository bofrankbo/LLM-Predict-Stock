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
from api import GeneticAlgorithm
from api import eval_on

class FactorUsableON(Factor):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env, count=1):

        self.env = env
        self.run_count = count
        self.path_folder = "FactorUsable"
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
        self.training_path = f"out_stock/Training_result/{self.path_folder}/{str(self.run_count)}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.similarity_threshold = 0.8    
    
    def generate_factors(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            return
        
        os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
        print(f"Generating factors for {stock_id}")
        res_factors_json = {}
        if country == 'tw':
            res_factors_json = {
                "1": "外部利好或政策支持：地緣政治緩和、政府支持或外部環境改善。",
                "2": "營收或財務表現：營收創高、超預期或低於預期。",
                "3": "市場情緒或經濟影響：市場樂觀或恐慌情緒、整體經濟放緩或改善。",
                "4": "競爭壓力：同業競爭加劇、其他公司表現優異、行業內的競爭加劇會影響市場份額和公司評估。",  
                "5": "產品創新與新技術發布：推出新產品或技術吸引投資者關注，提振市場信心。",
                "6": "市場情緒與分析師預測：投資者情緒和分析師的樂觀預測對股價波動具有顯著影響。",
                "7": "供應鏈與生產挑戰：生產流程中的供應鏈變動或延遲可能對公司股價造成負面影響。",
                "8": "內部重組與裁員動向：公司內部的結構調整、裁員或重組可能引發市場對穩定性的擔憂。"
            }
        elif country == 'us':
            res_factors_json = {
                "1": "External benefits or policy support: Geopolitical easing, government support, or improvement in external environments.",
                "2": "Revenue or financial performance: Record-high revenue, exceeding expectations, or falling short of expectations.",
                "3": "Market sentiment or economic impact: Optimistic or panicked market sentiment, overall economic slowdown, or improvement.",
                "4": "Competitive pressure: Intensified industry competition, exceptional performance by peers, or heightened competition within the industry affecting market share and company valuation.",
                "5": "Product innovation and new technology launches: Launching new products or technologies that attract investor attention and boost market confidence.",
                "6": "Market sentiment and analyst predictions: Investor sentiment and optimistic analyst forecasts have a significant impact on stock price fluctuations.",
                "7": "Supply chain and production challenges: Changes or delays in the supply chain during production processes may negatively impact the company's stock price.",
                "8": "Internal restructuring and layoff trends: Structural adjustments, layoffs, or reorganizations within the company may raise concerns about stability in the market."
            }

        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
        

    def run_taining(self, mode, train_datarange, test_datarange, eval_func):
        env = self.env
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        env['path_state'] = out_folder + '/state.json'
        env['path_gen'] = out_folder + '/generation_results.json'
        env['path_result']  = out_folder + '/result.json'

        # print("Start, 第一次跑的話請確認state是空的")
        ga = GeneticAlgorithm(env, self.price_his, train_datarange, eval_func, pop_size=20, generations=50, mode=mode, pop_len=len(factors.keys()))
        best_individual = ga.run()
        # print(f"Best individual: {best_individual}")

        individual = best_individual
        res_train = eval_func(env, individual, train_datarange, self.price_his)
        res_test = eval_func(env, individual, test_datarange, self.price_his)
        res = {
            "train": res_train,
            "test": res_test,
            "individual": individual,
        }
        # print(res)
        # print(file_result)
        with open(env['path_result'], 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)

        # print(res['test'])
        df = pd.DataFrame([res['train'], res['test']], index=['train', 'test'])

        return df