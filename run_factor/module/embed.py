import os
import json
import numpy as np
from sklearn.cluster import KMeans

from langchain_openai import OpenAIEmbeddings

class Embedding:
    def __init__(self, env, price_his):
        self.price_his = price_his
        self.env = env
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_embeddings = f"out_stock/Embeddings/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"

        # models
        self.embd_model = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
    def run(self):
        
        if os.path.exists(self.path_embeddings):
            with open(self.path_embeddings, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
            return np.array(embeddings)
        
        print("Factor Embd Generating factors...")
    
        news_titles = self.load_news_titles()
        
        return self.generate_embeddings(news_titles)
    
    
    # Step 1
    def load_news_titles(self):
        data = []
        with open(self.path_news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)

        for d in news_data.keys():
            for t in news_data[d]:
                headline = t.get("headline")
                data.append(headline)
        return data

    # Step 2
    def generate_embeddings(self, titles):
        embeddings = []
        for i in range(0, len(titles), 2000):  # 批量處理
            print(f"Generating embeddings for titles {i}/{len(titles)}")
            vector = self.embd_model.embed_documents(titles[i:i+2000])
            embeddings.extend(vector)
            # print(len(embeddings))
        os.makedirs(os.path.dirname(self.path_embeddings) , exist_ok=True)
        with open(self.path_embeddings, 'w', encoding='utf-8') as f:
            json.dump(embeddings, f, ensure_ascii=False, indent=4)
        return np.array(embeddings)
        
        
    