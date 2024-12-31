from api import eval
from api import genetic_algorithm
from api import factor_expanding

import os
import re
import json
import pandas as pd
from datetime import datetime, timedelta


class StockFactor:
    def __init__(self, llm, env):
        self.llm = llm
        self.env = env
        self.path_out = "out_stock/GA_factor_" + \
            env['start_date'] + "_" + env['end_date'] + "/"

    def get_news(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        # st,et 在 start_date, start_date 中約 3/4 之間
        st = start_date + \
            timedelta(days=(end_date - start_date).days * 3 / 4 - 15)
        et = start_date + timedelta(days=(end_date - start_date).days * 3 / 4)

        path_price = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{country}/stock_price/{stock_id}.csv"

        df_price_his = pd.read_csv(path_price, encoding='utf-8')
        df_price_his['Date'] = pd.to_datetime(
            df_price_his['Date'], format='%Y%m%d')
        df_price_his = df_price_his[(st <= df_price_his['Date']) & (
            df_price_his['Date'] <= et)]

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

    def run_factors(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')

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

            json_str = re.search(
                r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            with open(f"{self.path_out}{self.env['stock_id']}/factors.json", 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

        elif country == 'us':
            res_facotrs = self.llm(f"""
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
            "Convert these factors into this format; you only need to reply with the converted version.""")

            json_str = re.search(
                r'\{.*\}', res_factors_json.content, re.DOTALL).group()
            json_data = json.loads(json_str)
            with open(f"{self.path_out}{self.env['stock_id']}/factors.json", 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

    def run_factors_expand(self):
        factors = {}
        path_factors = f"{self.path_out}{self.env['stock_id']}/factors.json"
        # print(path_factors)
        if os.path.exists(path_factors):
            # print("Factors found")
            pass
        else:
            print("No factors found, process factors first")
            os.makedirs(os.path.dirname(path_factors), exist_ok=True)
            self.run_factors()

        with open(path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        # Access by index using list of keys
        key_list = list(factors.keys())
        value_list = list(factors.values())
        # print(key_list)
        # print(len(key_list))
        # print(len(value_list))

        # 讀取舊資料
        old_data = {}
        path_expand = f"{self.path_out}{self.env['stock_id']}/expand.json"
        os.makedirs(os.path.dirname(path_expand), exist_ok=True)
        if os.path.exists(path_expand):
            with open(path_expand, "r", encoding="utf-8") as f:
                old_data = json.load(f)

        data = factor_expanding(
            self.llm, self.env, key_list, value_list, old_data)

        # 儲存資料
        with open(path_expand, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def split_expand(self):
        env = self.env
        path_expand = f"{self.path_out}{self.env['stock_id']}/expand.json"
        # 解析日期
        start_day = datetime.strptime(env['start_date'], '%Y%m%d')
        end_day = datetime.strptime(env['end_date'], '%Y%m%d')

        # read train data
        with open(path_expand, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            data_points = json.loads(content)

        # split to training and testing
        total_days = (end_day - start_day).days + 1
        split_point = int(total_days * 3 / 4)
        training_end_day = start_day + timedelta(days=split_point - 1)
        testing_start_day = training_end_day + timedelta(days=1)
        train_datarange = {}
        for date_str, value in data_points["output_data"].items():
            date = datetime.strptime(date_str, '%Y%m%d')
            if start_day <= date <= training_end_day:
                train_datarange[date_str] = value
        test_datarange = {}
        for date_str, value in data_points["output_data"].items():
            date = datetime.strptime(date_str, '%Y%m%d')
            if testing_start_day <= date <= end_day:
                test_datarange[date_str] = value

        return train_datarange, test_datarange

    def run_taining(self, mode, train_datarange, test_datarange):
        env = self.env
        if mode == 0:
            out_folder = f"{self.path_out}{env['stock_id']}/ac"
        elif mode == 1:
            out_folder = f"{self.path_out}{env['stock_id']}/ev"
        path_factors = f"{self.path_out}{env['stock_id']}/factors.json"
        with open(path_factors, "r", encoding="utf-8") as f:
            factors = json.load(f)

        state_file = out_folder + '/state.json'
        file_gen = out_folder + '/generation_results.json'
        file_result = out_folder + '/result.json'

        # print("Start, 第一次跑的話請確認state是空的")
        best_individual = genetic_algorithm(factors, population_size=20, generations=50, state_file=state_file,
                                            results_file=file_gen, env=env, mode=mode, datarange=train_datarange)
        # print(f"Best individual: {best_individual}")

        individual = best_individual
        res_train = eval(individual, train_datarange, env)
        res_test = eval(individual, test_datarange, env)
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


# %%
# import os
# import json
# import pandas as pd
# from api import eval

# folders = os.listdir(env['path_out'])
# results = []
# index = []
# print(env['start_date'], env['end_date'])

# for folder in folders:
#     if folder == "factors_eng.json" or folder == "factors.json" or folder == "old_expand":
#         continue
#     folders_result = os.listdir(f"{env['path_out']}{folder}")
#     print(f"{folder}:")
#     for file in folders_result:
#         if file == "factors.json" or file == "expand.json" or file == "expand1.json" or file == "expand2.json":
#             continue
#         path = f"{env['path_out']}{folder}/{file}/generation_results.json"
#         with open(path, 'r') as f:
#             content = f.read().strip()
#         # print(file)
#         best_individual = []
#         for text in content.split('\n'):
#             data = json.loads(text)
#             best_individual = data['best_individual']

#         try:
#             individual = best_individual
#             print(f"{env['path_out']}{folder}/expand.json")
#             train_datarange, test_datarange = split_expand(env, f"{env['path_out']}{folder}/expand.json")
#             res_train = eval(individual, train_datarange)
#             res_test = eval(individual, test_datarange)
#             res = {
#                 "train": res_train,
#                 "test": res_test,
#                 "individual": individual,
#             }

#             file_result = f"{env['path_out']}{folder}/{file}/result.json"
#             print(file_result)
#             with open(file_result, 'w') as f:
#                 json.dump(res, f, ensure_ascii=False, indent=4)
#         except:
#             print("\tError")
#             pass
