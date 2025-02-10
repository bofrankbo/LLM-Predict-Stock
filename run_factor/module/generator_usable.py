import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

class UsableGenerator:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/FactorUsable/{env['stock_id']}/factors.json"    # 輸出 JSON 檔案
        
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
                "1": "外部利好或政策支持：地緣政治緩和、政府支持或外部環境改善。",
                "2": "營收或財務表現：營收創高、超預期或低於預期。",
                "3": "市場情緒或經濟影響：市場樂觀或恐慌情緒、整體經濟放緩或改善。",
                "4": "競爭壓力：同業競爭加劇、其他公司表現優異、行業內的競爭加劇會影響市場份額和公司評估。",  
                "5": "產品創新與新技術發布：推出新產品或技術吸引投資者關注，提振市場信心。",
                "6": "市場情緒與分析師預測：投資者情緒和分析師的樂觀預測對股價波動具有顯著影響。",
                "7": "供應鏈與生產挑戰：生產流程中的供應鏈變動或延遲可能對公司股價造成負面影響。",
                "8": "內部重組與裁員動向：公司內部的結構調整、裁員或重組可能引發市場對穩定性的擔憂。"
            }
        elif country == 'us':
            res_factors_json = {
                "1": "AI Innovations: Breakthroughs in AI models, chips, and foundational technologies.",
                "2": "Cloud & Data Center Investments: Major cloud and data center expansions globally.",
                "3": "Technological Leadership: Advancements in AI, security, and cutting-edge technologies.",
                "4": "Strategic Partnerships: Collaborations with major firms to enhance AI and cloud capabilities.",
                "5": "Energy Initiatives: Investments in nuclear and renewable energy for AI infrastructure.",
                "6": "Strong Earnings Reports: Favorable financial performance, especially in AI and cloud sectors.",
                "7": "Stock Splits & Market Cap Milestones: Events like stock splits and reaching $2T market cap.",
                "8": "Positive Analyst Ratings: Upgraded stock targets and bullish recommendations.",
                "9": "Institutional Investments: Large-scale hedge fund and ETF inflows.",
                "10": "Stock Buybacks & Insider Trading: Insider buying or selling trends indicating confidence.",
                "11": "Competitor Strengths: Rival companies gaining market share or surpassing valuations.",
                "12": "Product Criticism & AI Monetization Doubts: Concerns over practical value and revenue generation.",
                "13": "Regulatory & Legal Scrutiny: Government probes and lawsuits impacting business operations.",
                "14": "Macroeconomic & Geopolitical Factors: Interest rates, economic slowdowns, and AI export restrictions.",
                "15": "Sector Competition & AI Market Share: Growing competition in AI and cloud services."
            }

        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
            
        return res_factors_json