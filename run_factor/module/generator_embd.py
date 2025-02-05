import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from sklearn.cluster import KMeans
from langchain_openai import ChatOpenAI

from .generator import FactorGenerator

class GeneratorEmbd(FactorGenerator):
    '''
        Implement from FactorGenerator
        Generate cluster summaries and factors
    '''
    
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_factors = f"out_stock/Factors/{self.path_out}/factors.json"    # 輸出 JSON 檔案
        self.path_clustered_summaries = f"out_stock/Cluster_summmaries/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"

        # setting
        self.llm4o = ChatOpenAI(
            openai_api_key = os.getenv('OPENAI_API_KEY'),
            model='gpt-4o',
            temperature=1,
        )
        
    def generate_factors(self, representative_titles):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        # start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        # end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            with open(self.path_factors, 'r', encoding='utf-8') as f:
                factor_data = json.load(f)
            return factor_data
        
        # print(f"Generating factors for {stock_id}")
        # if not os.path.exists(self.path_clustered_summaries):
        #     print("Factor Embd Generating factors...")
        #     # Step 1: 載入新聞標題
        #     news_titles = self.load_news_titles()
            
        #     # Step 2: 生成嵌入向量
        #     embeddings = self.generate_embeddings(news_titles, embd_model)
            
        #     # Step 3: 分群
        #     kmeans, labels = self.cluster_titles_kmeans(embeddings)
            
        #     # Step 4: 找出代表標題
        #     representative_titles = self.extract_representative_titles(news_titles, embeddings, kmeans, labels)
            
        #     self.save_cluster(representative_titles, self.path_clustered_summaries)
        
        # representative_titles = self.load_cluser(self.path_clustered_summaries)
        
        for label, cluster in representative_titles.items():
            news = f"{cluster['representative']}"
            for i, title in enumerate(cluster['titles']):
                if i >= 20:
                    break
                news += f"  - {title}\n"
                            
        if country == 'tw':
            res_facotrs = self.llm4o.invoke(f"""
            以下的新聞出現後隔日{stock_name}的股價波動有關：
            『{news}』

            請依據上述的新聞列出20個會造成股價波動的可能原因，
            以台灣中文回答""")

            res_factors_json = self.llm4o.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            把這些因素轉換成這樣的格式，你只需要回答我轉換後的樣子就好""")

            json_str = re.search(r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
            with open(self.path_factors, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

        elif country == 'us':
            res_facotrs = self.llm4o.invoke(f"""
            The following news is related to the stock price fluctuation of {stock_name} the next day
            "{news}"

            Please list 20 possible reasons for stock price fluctuations based on the above news.""")

            res_factors_json = self.llm4o.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            "Convert these factors into this format; you only need to reply with the converted version.""")

            json_str = re.search(r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
            with open(self.path_factors, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            
            
    