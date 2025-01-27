import os
from module.factor_expanding import FactorExpanding

# 儲存的日期是判斷日期，非新聞日期
# 以判斷日期為準
class UsableExpanding(FactorExpanding):
    def __init__(self, env, llm, price_his):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_expand = f"out_stock/Expands/{env['path_folder']}/{env['stock_id']}/expand.json"    # 輸出 JSON 檔案
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"