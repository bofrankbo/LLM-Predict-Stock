from api import eval
from api import genetic_algorithm
from api import factor_expanding
from api import split_expand

import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


class StockFactor:
    def __init__(self, env):
        self.env = env
        self.path_folder = "out_stock/GA_factor_"
        self.path_out = self.path_folder + env['start_date'] + "_" + env['end_date'] + "/" + env['stock_id'] + "/"
        self.path_factors = f"{self.path_out}factors.json"
        self.path_expand = f"{self.path_out}expand.json"
        self.price_his = self.get_price_his()
        
    def get_price_his(self):
        country = self.env['country']
        stock_id = self.env['stock_id']
        path_price_his = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{country}/stock_price/{stock_id}.csv"
        df_price_his = pd.read_csv(path_price_his, encoding="utf-8")
        df_price_his["Date"] = pd.to_datetime(df_price_his["Date"], format="%Y%m%d")
        return df_price_his
    
    def get_factors(self):
        if os.path.exists(self.path_factors):
            with open(self.path_factors, "r", encoding="utf-8") as f:
                factors = json.load(f)
            return factors
        else:
            print("No factors found, Please process Factors first")
            return

    def get_expand(self, show_sig=False):
        
        if os.path.exists(self.path_expand):
            with open(self.path_expand, "r", encoding="utf-8") as f:
                expand_data = json.load(f)
        else:
            print("No expand data found, Please process Factors first")
            return
        
        if show_sig:
            key = expand_data["output_data"].keys()
            for k in key:
                print(f"{k.rjust(10)} => ", end="")
                for k2 in expand_data["output_data"][k]["skeleton"].keys():
                    print(f"{str(expand_data['output_data'][k]['skeleton'][k2]['sig']).rjust(3)}", end=" ")
                print()
                
        return expand_data
    
    def get_individual(self, mode):
        env = self.env
        if mode == 0:
            out_folder = f"{self.path_out}ac"
        elif mode == 1:
            out_folder = f"{self.path_out}ev"
        
        with open(f"{out_folder}/result.json", "r", encoding="utf-8") as f:
            res = json.load(f)
            individual = res['individual']
        
        return individual

        
    def get_news(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        # st,et 在 start_date, start_date 中約 3/4 之間
        st = start_date + timedelta(days=(end_date - start_date).days * 3 / 4 - 15)
        et = start_date + timedelta(days=(end_date - start_date).days * 3 / 4)

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

    def generate_factors(self, llm):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            return
        
        print(f"Generating factors for {stock_id}")
        os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
        news_rise, news_fall = self.get_news()

        if country == 'tw':
            res_facotrs = llm.invoke(f"""
            以下的新聞出現後隔日{stock_name}的股價上漲
            『{news_rise}』

            以下的新聞出現後{stock_name}的股價下跌
            『{news_fall}』

            請依據{stock_name}新聞比較兩者的不同
            列出10個在上漲會出現的可能原因
            再幫我列出10個下跌可能會出現的原因.""")

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
            After the following news, {stock_name}'s stock price rose the next day:
            『{news_rise}』

            After the following news, {stock_name}'s stock price fell:
            『{news_fall}』

            Please compare the differences between the two sets of news for {stock_name}.

            List 10 possible reasons for the price increase and another 10 possible reasons for the price decrease.""")

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

    def expand_factors(self, llm_factors):
        '''
            llm_factors: list of factors
            
            update factors.json
            it can generate new factors while old factors are not empty
            if old data is empty, then create a new one
        '''
        
        factors = self.get_factors()
        key_list = list(factors.keys())
        value_list = list(factors.values())

        old_data = {}
        if os.path.exists(self.path_expand):
            with open(self.path_expand, "r", encoding="utf-8") as f:
                old_data = json.load(f)

        data = factor_expanding(llm_factors, self.env, key_list, value_list, old_data)

        # 儲存資料
        with open(self.path_expand, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def run_taining(self, mode, train_datarange, test_datarange, re_run=False):
        env = self.env
        if mode == 0:
            out_folder = f"{self.path_out}ac"
        elif mode == 1:
            out_folder = f"{self.path_out}ev"
        
        if re_run:
            if os.path.isdir(out_folder):
                shutil.rmtree(out_folder)
            elif os.path.isfile(out_folder):
                os.remove(out_folder)
            
        with open(self.path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        state_file = out_folder + '/state.json'
        file_gen = out_folder + '/generation_results.json'
        file_result = out_folder + '/result.json'

        # print("Start, 第一次跑的話請確認state是空的")
        best_individual = genetic_algorithm(factors, state_file, file_gen, train_datarange, self.price_his, population_size=20, generations=50, mode=mode)
        # print(f"Best individual: {best_individual}")

        individual = best_individual
        res_train = eval(individual, train_datarange, self.price_his)
        res_test = eval(individual, test_datarange, self.price_his)
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
    
    def split_exp(self):
        return split_expand(self.env, self.path_expand)
        
    
    def plot_acumulated_return(self, date_ranges=None):
        env = self.env
        if date_ranges is None:
            date_ranges = [
                [self.env['start_date'], self.env['end_date']]
            ]
        df_price_his = self.price_his
        list_bnh_rtn = []
        list_factor_rtn = []
        list_date = []

        path_out_rtn1 = self.path_folder + date_ranges[0][0] + "_" + date_ranges[0][1] + "/" + env['stock_id'] + "/"
        with open(f"{path_out_rtn1}ev/result.json", 'r') as f:
                res = json.load(f)
                res_test = res['test']
            
        balance = df_price_his[df_price_his['Date'].dt.strftime('%Y%m%d') == res_test["rtn_list"][0][0]]['Open'].values[0]
        
        for date_range in date_ranges:
            path_out_rtn = self.path_folder + date_range[0] + "_" + date_range[1] + "/" + env['stock_id'] + "/"
            # 顯示回測結果
            with open(f"{path_out_rtn}ev/result.json", 'r') as f:
                res = json.load(f)
                res_test = res['test']

            for date, rtn in res_test['rtn_list']:
                # print(rtn)
                balance = balance * (1 + float(rtn))
                list_date.append(date)
                list_bnh_rtn.append(df_price_his[df_price_his['Date'].dt.strftime(
                    '%Y%m%d') == date]['Close'].values[0])
                list_factor_rtn.append(balance)

        df = pd.DataFrame(list_factor_rtn, index=list_date, columns=['balance'])
        dplot = [datetime.strptime(d, '%Y%m%d').date() for d in list_date]

        plt.title(f" {env['stock_id']} trading results")
        plt.plot(dplot, list_bnh_rtn, label="buy and hold")  # blue
        plt.plot(dplot, list_factor_rtn, label="factor trading")  # orange
        plt.show()