import os
import json
import numpy as np
from sklearn.cluster import KMeans

class Embedding:
    def __init__(self, env, price_his):
        self.price_his = price_his
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.path_embeddings = f"out_stock/Embeddings/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        self.path_clustered_summaries = f"out_stock/Cluster_summmaries/{self.path_out}/embeddings.json"    # 輸出 JSON 檔案
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
  
    # Step 1: 載入新聞標題 JSON
    def load_news_titles(self):
        data = []
        with open(self.path_news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
            news_stock = ''
        for d in news_data.keys():
            for t in news_data[d]:
                headline = t.get("headline")
                data.append(headline)
        return data

    # Step 2: 生成嵌入向量
    def generate_embeddings(self, titles, embeddings_model):
        if os.path.exists(self.path_embeddings):
            with open(self.path_embeddings, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
            return np.array(embeddings)
        
        embeddings = []
        for i in range(0, len(titles), 2000):  # 批量處理
            print(f"Generating embeddings for titles {i}/{len(titles)}")
            vector = embeddings_model.embed_documents(titles[i:i+2000])
            embeddings.extend(vector)
            # print(len(embeddings))
        os.makedirs(os.path.dirname(self.path_embeddings) , exist_ok=True)
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
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
    def load_cluser(self, output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)