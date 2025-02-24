from eval.eval_on_long import EvalONLong
from eval.eval_daytrade import EvalDayTrade

class EvalMix2:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        
    def binary_to_decimal(self, individual):
        last_8_bits = individual[-8:]  # 取得最後8個數字
        binary_str = ''.join(map(str, last_8_bits))  # 轉換成字串
        decimal_value = int(binary_str, 2)  # 轉換成十進位
        return str(decimal_value)
    
    def eval(self, datarange, individual):
        self.MOV = 'EMA' + self.binary_to_decimal(individual)
        # 檢查 price_his 中 Close 欄位是否大於 self.MOV 欄位
        df_price_his = self.price_his
        df_price_his['Close'] = df_price_his['Close'].astype(float)
        df_price_his[self.MOV] = df_price_his[self.MOV].astype(float)
        df_price_his = df_price_his.dropna()
        df_price_his = df_price_his.reset_index(drop=True)
        upperthenema = 0
        for row in df_price_his:
            if float(row['Close']) > float(row[self.MOV]):
                upperthenema += 1
        if upperthenema > len(df_price_his)/2:
            print("多頭做 ON Long 策略")
            self.eval_mode = "ON_Long"
            self.eval_module = EvalONLong(self.env, self.price_his)
        else:
            print("空頭做 Day Trade 策略")
            self.eval_mode = "Day_Trade"
            self.eval_module = EvalDayTrade(self.env, self.price_his)
        
        res = self.eval_module.eval(self.date_range, self.individual)
        return res