import os
import re
import json
import shutil
import numpy as np
import pandas as pd
from openai import OpenAI
from sklearn.cluster import KMeans
from datetime import datetime

from factor import Factor
from api import genetic_algorithm_on
from api import eval_on


class FactorEmbOverNight(Factor):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env, count=1):
        # 初始化 OpenAI API
        self.client = OpenAI()
        self.client.api_key = os.getenv('OPENAI_API_KEY')
        self.env = env
        
        # 固定的資料路徑
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.price_his = self.get_price_his()
        
        # 輸出的路徑
        self.path_folder = "EmbdON"
        self.path_out =  f"{self.path_folder}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_embeddings = f"out_stock/Embeddings/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        self.path_clustered_summaries = f"out_stock/Cluster_summmaries/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        self.path_factors = f"out_stock/Factors/{self.path_out}/factors.json"    # 輸出 JSON 檔案
        self.path_expand = f"out_stock/Expands/{self.path_out}/expand.json"    # 輸出 JSON 檔案
        self.training_path = f"out_stock/Training_result/{self.path_folder}/{env['start_date']}_{env['end_date']}/{str(count)}/{env['stock_id']}"
        
        self.similarity_threshold = 0.8  # 語意相似度閾值
        
    # Step 1: 載入新聞標題 JSON
    def load_news_titles(self, file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
            news_stock = ''
        for d in news_data.keys():
            for t in news_data[d]:
                headline = t.get("headline")
                data.append(headline)
        return data

    # Step 2: 生成嵌入向量
    def generate_embeddings(self, titles):
        if os.path.exists(self.path_embeddings):
            with open(self.path_embeddings, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
            return np.array(embeddings)
        
        embeddings = []
        for i in range(0, len(titles), 2000):  # 批量處理
            print(f"Generating embeddings for titles {i}/{len(titles)}")
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=titles[i:i+2000]
            )
            embeddings.extend([e.embedding for e in response.data])
        os.makedirs(self.path_out, exist_ok=True)
        with open(self.path_embeddings, 'w', encoding='utf-8') as f:
            json.dump(embeddings, f, ensure_ascii=False, indent=4)
        return np.array(embeddings)

    # Step 3: 分群
    def cluster_titles_kmeans(self, embeddings, n_clusters=20):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        return kmeans, labels

    # Step 4: 找出代表標題
    def extract_representative_titles(self, titles, embeddings, kmeans, labels):
        clusters = {i: [] for i in range(kmeans.n_clusters)}
        for label, title, embedding in zip(labels, titles, embeddings):
            clusters[label].append((title, embedding))
        
        representative_titles = {}
        for label, items in clusters.items():
            cluster_center = kmeans.cluster_centers_[label]
            # 找出距離群中心最近的標題
            closest_title = min(
                items, key=lambda x: np.linalg.norm(np.array(x[1]) - cluster_center)
            )[0]
            representative_titles[label] = {
                "representative": closest_title,
                "titles": [item[0] for item in items]
            }
        return representative_titles

    # Step 5: 儲存結果
    def save_cluster(self, results, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
    def load_cluser(self, output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_factors(self, llm):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            return
        
        print(f"Generating factors for {stock_id}")
        if not os.path.exists(self.path_clustered_summaries):
            print("Factor Embd Generating factors...")
            # Step 1: 載入新聞標題
            news_titles = self.load_news_titles(self.path_news_file)
            
            # Step 2: 生成嵌入向量
            embeddings = self.generate_embeddings(news_titles)
            
            # Step 3: 分群
            kmeans, labels = self.cluster_titles_kmeans(embeddings)
            
            # Step 4: 找出代表標題
            representative_titles = self.extract_representative_titles(news_titles, embeddings, kmeans, labels)
            
            self.save_cluster(representative_titles, self.path_clustered_summaries)
        
        representative_titles = self.load_cluser(self.path_clustered_summaries)
        for label, cluster in representative_titles.items():
            news = f"{cluster['representative']}"
            for i, title in enumerate(cluster['titles']):
                if i >= 20:
                    break
                news += f"  - {title}\n"
                            
        if country == 'tw':
            res_facotrs = llm.invoke(f"""
            以下的新聞出現後隔日{stock_name}的股價波動有關：
            『{news}』

            請依據上述的新聞列出20個會造成股價波動的可能原因，
            以台灣中文回答""")

            res_factors_json = llm.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            把這些因素轉換成這樣的格式，你只需要回答我轉換後的樣子就好""")

            json_str = re.search(
                r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            with open(self.path_factors, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

        elif country == 'us':
            res_facotrs = llm.invoke(f"""
            The following news is related to the stock price fluctuation of {stock_name} the next day
            "{news}"

            Please list 20 possible reasons for stock price fluctuations based on the above news.""")

            res_factors_json = llm.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            "Convert these factors into this format; you only need to reply with the converted version.""")

            json_str = re.search(
                r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            with open(self.path_factors, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    def run_taining(self, mode, train_datarange, test_datarange):
        env = self.env
        if mode == 0:
            out_folder = f"{self.training_path}/ac"
        elif mode == 1:
            out_folder = f"{self.training_path}/ev"
        
        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        state_file = out_folder + '/state.json'
        file_gen = out_folder + '/generation_results.json'
        file_result = out_folder + '/result.json'

        # print("Start, 第一次跑的話請確認state是空的")
        best_individual = genetic_algorithm_on(factors, state_file, file_gen, train_datarange, self.price_his, population_size=20, generations=50, mode=mode)
        # print(f"Best individual: {best_individual}")

        individual = best_individual
        res_train = eval_on(individual, train_datarange, self.price_his)
        res_test = eval_on(individual, test_datarange, self.price_his)
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