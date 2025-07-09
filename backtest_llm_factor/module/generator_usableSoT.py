import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class UsableSoTGenerator:
    def __init__(self, env, price_his):
        self.env = env
        self.country = env['country']
        self.price_his = price_his
        self.path_factors = f"{os.getcwd()}/backtest_llm_factor/out_stock/Factors/UsableSoT/factors_{self.country}.json"
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
    
    def generate_factors(self):
        stock_id = self.env['stock_id']
        stock_name = self.env['stock_name']
        country = self.env['country']
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        
        if os.path.exists(self.path_factors):
            return json.load(open(self.path_factors, 'r', encoding='utf-8'))
        
        os.makedirs(os.path.dirname(self.path_factors), exist_ok=True)
        print(f"Generating factors for {stock_id}")
        res_factors_json = {}
        if country == 'tw':
            res_factors_json = {
                "1": "外部利好或政策支持",
                "2": "營收或財務表現",
                "3": "市場情緒或經濟影響",
                "4": "競爭壓力",
                "5": "產品創新與新技術發布",
                "6": "市場情緒與分析師預測",
                "7": "供應鏈與生產挑戰",
                "8": "內部重組與裁員動向",
                "9": "資金流動與外資動向",
                "10": "貨幣政策與利率變動",
                "11": "產業景氣循環",
                "12": "企業併購與合作",
                "13": "法律與監管風險",
                "14": "市場黑天鵝事件",
                "15": "ESG（環境、社會、治理）影響",
                "16": "股利政策與回購計畫",
                "17": "供應鏈備貨與庫存調整",
                "18": "工廠稼動率變動",
                "19": "短期訂單波動",
                "20": "物流成本上升",
                "21": "勞動力短缺或薪資調整",
                "22": "內部成本控制策略",
                "23": "原物料短期價格波動",
                "24": "關鍵零件缺貨或供應短缺",
                "25": "季節性銷售波動",
                "26": "短期促銷與折扣策略",
                "27": "消費者信心短期變化",
                "28": "熱門話題或社群媒體影響",
                "29": "技術故障或生產意外",
                "30": "競爭對手價格戰",
                "31": "短期內部消息流出",
                "32": "企業短期融資需求",
                "33": "市場短期交易量異常變動",
                "34": "特定機構或基金大筆買賣",
                "35": "新市場或通路開拓進度",
                "36": "內部高層短期人事變動",
                "37": "短期政策或補助變動",
                "38": "短期投資人情緒過熱或恐慌",
                "39": "短線交易或市場操縱行為",
                "40": "品牌或產品公關危機",
                "41": "天氣或自然災害影響",
                "42": "短期政府或央行發言影響"
            }
        elif country == 'us':
            res_factors_json = {
                "1": "External benefits or policy support: Geopolitical easing, government support, or improvement in external environments.",
                "2": "Revenue or financial performance: Record-high revenue, exceeding expectations, or falling short of expectations.",
                "3": "Market sentiment or economic impact: Optimistic or panicked market sentiment, overall economic slowdown, or improvement.",
                "4": "Competitive pressure: Intensified industry competition, exceptional performance by peers, or heightened competition within the industry affecting market share and company valuation.",
                "5": "Product innovation and new technology launches: Launching new products or technologies that attract investor attention and boost market confidence.",
                "6": "Market sentiment and analyst predictions: Investor sentiment and optimistic analyst forecasts have a significant impact on stock price fluctuations.",
                "7": "Supply chain and production challenges: Changes or delays in the supply chain during production processes may negatively impact the company's stock price.",
                "8": "Internal restructuring and layoff trends: Structural adjustments, layoffs, or reorganizations within the company may raise concerns about stability in the market."
            }

        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
    
    def get_factors(self, factors_count):
        factors = json.load(open(self.path_factors, 'r', encoding='utf-8'))
        new_factors = {}
        for i in range(factors_count):
            new_factors[str(i+1)] = factors[str(i+1)]
        return new_factors