import os
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from news_title import NewsCrawler
from module import ExpandIndexRun
from module import Generator_Index
from eval import EvalDayTrade
from module import GeneticAlgorithm

class Predictor:
    def __init__(self, env):
        pass
        self.env = env
        self.price_his = self.get_price_his()
        # self.exp_data = self.llm.get_exp_data
        
    def run(self):
        self.crawl()
        self.generate_sig()
        quarter_dates, last_3q_dates, year_dates = self.get_last_quarter_and_past_year_dates()

        upperthenema = 0
        mask = self.price_his['Date'].apply(lambda d: d.strftime("%Y%m%d") in quarter_dates)
        dates = self.price_his.loc[mask]
        for index, row in dates.iterrows():
            if float(row['Close']) > float(row['EMA60']):
                upperthenema += 1
        
        self.env['start_date'] = year_dates[0]
        self.env['end_date'] = year_dates[-1]
        self.env['path_folder'] = "FactorUsableMix"
        self.env['run_count'] = 1
        
        self.eval_module = EvalDayTrade(self.env, self.price_his)
        self.trade_type = "day_trade"
        
        self.individual = self.get_individual()
        return  self.get_trade_sig()
        
    
    def get_price_his(self):
        country = self.env['country']
        stock_id = self.env['stock_id']
        path_price_his = f"{os.getcwd()}/history_data/{country}/stock_price/{stock_id}tech.csv"
        # print(path_price_his)
        df_price_his = pd.read_csv(path_price_his, encoding="utf-8")
        df_price_his["Date"] = pd.to_datetime(df_price_his["Date"], format="%Y%m%d")
        return df_price_his
    
    def crawl(self):

        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() - timedelta(days=1)

        data = [
            ["2308", "台達電", "tw"],
            ["2317", "鴻海", "tw"],
            ["2330", "台積電", "tw"],
            ["2382", "廣達", "tw"],
            ["2412", "中華電", "tw"],
            ["2454", "聯發科", "tw"],
            ["2881", "富邦金", "tw"],
            ["2882", "國泰金", "tw"],
            ["2891", "中信金", "tw"],
            ["6505", "台塑化", "tw"],
        ]

        crawler = NewsCrawler(start_date, end_date, data)
        crawler.run()
        
    def generate_sig(self):
        fac_module = Generator_Index(self.env)
        self.factors = fac_module.generate_factors()
        exp_module = ExpandIndexRun(self.env, datetime.now(), self.price_his)
        exp_module.expanding(factors=self.factors)
    
    def get_last_quarter_and_past_year_dates(self):
        today = datetime.today()
        current_month = today.month
        current_year = today.year

        # 計算上一季的起始月份與年份
        if current_month in [1, 2, 3]:  # Q1 → 上一季為 Q4
            start_month, year = 10, current_year - 1
        elif current_month in [4, 5, 6]:  # Q2 → 上一季為 Q1
            start_month, year = 1, current_year
        elif current_month in [7, 8, 9]:  # Q3 → 上一季為 Q2
            start_month, year = 4, current_year
        else:  # Q4 → 上一季為 Q3
            start_month, year = 7, current_year

        # 上一季的開始日期
        start_quarter_date = datetime(year, start_month, 1)
        end_quarter_date = start_quarter_date + relativedelta(months=3)
        
        # 上三季的開始日期
        start_3quarter_date = start_quarter_date - relativedelta(months=6)

        # 本季結束日期的前一年
        past_year_start = end_quarter_date - relativedelta(months=9)

        # 取得日期範圍
        last_quarter_dates = pd.date_range(start=start_quarter_date, end=end_quarter_date - timedelta(days=1)).strftime("%Y%m%d").tolist()
        last_3quarter_dates = pd.date_range(start=start_3quarter_date, end=end_quarter_date - timedelta(days=1)).strftime("%Y%m%d").tolist()
        year_dates = pd.date_range(start=past_year_start, end=end_quarter_date + relativedelta(months=3) - timedelta(days=1)).strftime("%Y%m%d").tolist()   
        return last_quarter_dates, last_3quarter_dates, year_dates

    
    def get_individual(self):
        quarter_dates, last_3quarter_dates, year_dates = self.get_last_quarter_and_past_year_dates()
        mask = self.price_his['Date'].apply(lambda d: d.strftime("%Y%m%d") in last_3quarter_dates)
        dates = self.price_his.loc[mask]
        # 將 Date 欄位轉換成字典，格式為 {"YYYYMMDD": ""}
        date_dict = dict.fromkeys(dates['Date'].apply(lambda d: d.strftime("%Y%m%d")), "")
        with open(f"{os.getcwd()}/run_td/out_stock/Expands/UsableDT/tx/expand.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            exp_data = data['output_data']
        # 找到 和 exp_data 日期相同的資料
        for key in exp_data.keys():
            if key in date_dict:
                date_dict[key] = exp_data[key]
        
        mode = 1
        res = self.eval_module.load_result(mode)
        if res == None:
            ga = GeneticAlgorithm(self.env, self.price_his, date_dict, self.eval_module.eval, pop_size=20, generations=50, mode=mode, pop_len=len(self.factors.keys()))
            individual = ga.run()
        
            res_train = self.eval_module.eval(date_dict, individual)
            res = {
                "train": res_train,
                "individual": individual,
            }
            self.eval_module.save_result(res, mode)
        return res['individual']
    
    def get_trade_sig(self):
        with open(f"{os.getcwd()}/run_td/out_stock/Expands/UsableDT/tx/expand.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            exp_data = data['output_data']
        
        sig_data = {datetime.now().strftime("%Y%m%d") : exp_data[datetime.now().strftime("%Y%m%d")]}

        # print(sig_data.values())
        list_sig = self.eval_module.get_sigs(sig_data, self.individual)
        print(list_sig[0][1])
        
        # type 當沖 or 持有
        # sig 交易的方向
        trade = {
            'sig' : list_sig[0][1],
            'type' : self.trade_type,
        }
        
        return trade