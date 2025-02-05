import os
import re
import json
import shutil
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime

from factor import Factor

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from module import Embedding
from module import GeneratorEmbd
from module import FactorExpanding
from module import GeneticAlgorithm
from eval.eval_overnight import EvalOvernight


class FactorEmbdON(Factor):
    '''
        Implement from Factor
        Change the factor generating function from factor
        First embed the news title and cluster them then generate factors
    '''
    def __init__(self, env):
        self.env = env
        self.run_count = env['run_count']
        self.path_folder = "EmbdON"
        self.env['path_folder'] = self.path_folder
        
        # output path
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{self.path_folder}/{str(self.run_count)}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_clustered_summaries = f"out_stock/Cluster_summmaries/{self.path_out}/embeddings.json"  
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
  
        # get history data
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
        self.price_his = self.get_price_his()

        # setting
        self.similarity_threshold = 0.8

        self.llm = ChatOpenAI(
            openai_api_key = os.getenv('OPENAI_API_KEY'),
            model='gpt-4o-mini',
            temperature=1,
        )
        
    def run(self):
        
        # embed
        module_embd = Embedding(self.env, self.price_his)
        embeddings = module_embd.run()
        
        # cluster
        if os.path.exists(self.path_clustered_summaries):
            representative_titles = self.load_cluser(self.path_clustered_summaries)
        else:
            news_titles = self.load_news_titles()
            kmeans, labels = self.cluster_titles_kmeans(embeddings)
            representative_titles = self.extract_representative_titles(news_titles, embeddings, kmeans, labels)
            self.save_cluster(representative_titles, self.path_clustered_summaries)
        
        # generate factors
        module_gen = GeneratorEmbd(self.env, self.price_his)
        module_exp = FactorExpanding(self.env, self.llm, self.price_his)
        self.factors = module_gen.generate_factors(representative_titles)
        self.exp_data = module_exp.expanding(self.factors)
    
    def training(self, mode, train_datarange, test_datarange):
        eval_module = EvalOvernight(self.env, self.price_his)
        ga = GeneticAlgorithm(self.env, self.price_his, train_datarange, eval_module.eval, pop_size=20, generations=50, mode=mode, pop_len=len(self.factors.keys()))
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
    
    def load_news_titles(self):
        data = []
        with open(self.path_news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        for d in news_data.keys():
            for t in news_data[d]:
                headline = t.get("headline")
                data.append(headline)
        return data

    def cluster_titles_kmeans(self, embeddings, n_clusters=20):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        return kmeans, labels

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

    def save_cluster(self, results, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
    def load_cluser(self, output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)

