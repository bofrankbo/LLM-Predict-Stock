import pandas as pd
from datetime import datetime

from eval.eval_on_long import EvalONLong
from eval.eval_daytrade import EvalDayTrade

class EvalMix2(EvalDayTrade):
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_out =  f"{env['path_folder']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        self.training_path = f"out_stock/Training_result/{env['path_folder']}/{env['run_count']}/{env['start_date']}_{env['end_date']}/{env['stock_id']}"
        
        
    def binary_to_decimal(self, individual):
        last_8_bits = individual[-8:]  # 取得最後8個數字
        binary_str = ''.join(map(str, last_8_bits))  # 轉換成字串
        decimal_value = int(binary_str, 2)  # 轉換成十進位
        return str(decimal_value + 1)
    
    def eval(self, datarange, individual):
        self.MOV = 'EMA' + self.binary_to_decimal(individual)
        # 檢查 price_his 中 Close 欄位是否大於 self.MOV 欄位
        df_price_his = self.price_his
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        df_price_his = df_price_his[(df_price_his['Date'] >= start_date) & (df_price_his['Date'] <= end_date)]
        # 取得前一季的所有價格資料
        n = len(df_price_his) // 4  # 取整數部分
        
        df_price_his = df_price_his.iloc[-2*n:-n]
        upperthenema = 0
        # interate through df_price_his
        for index, row in df_price_his.iterrows():
            if float(row['Close']) > float(row[self.MOV]):
                upperthenema += 1
                
        if upperthenema > len(df_price_his)/2:
            # print("多頭做 ON Long 策略")
            self.eval_mode = "ON_Long"
            self.eval_module = EvalONLong(self.env, self.price_his)
        else:
            # print("空頭做 Day Trade 策略")
            self.eval_mode = "Day_Trade"
            self.eval_module = EvalDayTrade(self.env, self.price_his)
        
        res = self.eval_module.eval(datarange, individual[:42])
        return res