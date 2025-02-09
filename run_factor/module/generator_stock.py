import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

class FactorGenerator:
    def __init__(self, env, price_his, llm):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/Factor/{env['start_date']}_{env['end_date']}/{env['stock_id']}/factors.json"    # 輸出 JSON 檔案
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
    
    def get_news(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        # st,et 在 start_date, start_date 中約 3/4 之間
        st = start_date + timedelta(days=(end_date - start_date).days * 3 / 4 - 15)
        et = start_date + timedelta(days=(end_date - start_date).days * 3 / 4)

        df_price_his = self.price_his.copy()
        df_price_his['Date'] = pd.to_datetime(self.price_his['Date'], format='%Y%m%d')
        df_price_his = df_price_his[(st <= df_price_his['Date']) & (self.price_his['Date'] <= et)]

        news_rise = ''
        news_fall = ''
        for index, row in df_price_his.iterrows():
            news_daily = ""
            path_news_title = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{country}/news_title/{stock_id}news_title.json"

            news_date = row['Date']
            last_day = row['Date'] - timedelta(days=1)
            rtn = (row['Close'] - row['Open']) / row['Open']

            with open(path_news_title, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
                news_stock = ''
                for t in news_data[last_day.strftime('%Y%m%d')]:
                    headline = t.get("headline")
                    # content = t.get("content")
                    news_stock += f"{headline}.  "
                    # 刪掉t的換行符號
                    news_stock = news_stock.replace('\n', '')
                    # 刪除股價名稱還有
                    # t = t.replace(stock_name, f'company')
                    # news_stock += ','
                    # 最後一個逗號刪掉
                news_stock = news_stock[:-1]
                news_daily += f"{news_stock}"

            if rtn > 0:
                # news += f"rtn: {round(rtn,5)}, {news_daily}\n"
                news_rise += f"{news_daily}\n"

            if rtn < 0:
                # news += f"rtn: {round(rtn,5)}, {news_daily}\n"
                news_fall += f"{news_daily}\n"

        return news_rise, news_fall
    
    def generate_factors(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            with open(self.path_factors, 'r', encoding='utf-8') as f:
                factor_data = json.load(f)
            return factor_data
        
        print(f"Generating factors for {stock_id}")
        os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
        news_rise, news_fall = self.get_news()

        if country == 'tw':
            res_facotrs = self.llm.invoke(f"""
            以下的新聞出現後隔日{stock_name}的股價上漲
            『{news_rise}』

            以下的新聞出現後{stock_name}的股價下跌
            『{news_fall}』

            請依據{stock_name}新聞比較兩者的不同
            列出10個在上漲會出現的可能原因
            再幫我列出10個下跌可能會出現的原因.""")

            res_factors_json = self.llm.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            把這些因素轉換成這樣的格式，你只需要回答我轉換後的樣子就好""")

        elif country == 'us':
            res_facotrs = self.llm.invoke(f"""
            After the following news, {stock_name}'s stock price rose the next day:
            『{news_rise}』

            After the following news, {stock_name}'s stock price fell:
            『{news_fall}』

            Please compare the differences between the two sets of news for {stock_name}.

            List 10 possible reasons for the price increase and another 10 possible reasons for the price decrease.""")

            res_factors_json = self.llm.invoke(res_facotrs.content + """
            {
                "1": "xxx：xxxxx"
                "2": 
                "3": 
                "4": 
                ...
                "20":
            }
            "Convert these 20 factors into this format; you only need to reply with the converted version.""")
            


        json_str = re.search(r'\{.*\}', res_factors_json.content, re.DOTALL).group()
        factor_data = json.loads(json_str)
        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(factor_data, f, ensure_ascii=False, indent=4)
        
        if len(factor_data.keys()) != 20:
            print("Error: factors error")
            
        return factor_data
            
            
    