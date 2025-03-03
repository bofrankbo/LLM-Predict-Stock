import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

class GeneratorF24:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/F24/{env['stock_id']}/factors.json"    # 輸出 JSON 檔案
        
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
                "8": "內部重組與裁員動向：公司內部的結構調整、裁員或重組可能引發市場對穩定性的擔憂。",                
                "9": "外部利多或政策支持：政策調整、經濟刺激方案、產業補助對企業的影響。",
                "10": "地緣政治緩和：國際關係趨穩，降低市場不確定性，影響投資信心。",
                "11": "政府補貼或稅收優惠：財政支持如何影響企業經營成本與競爭優勢。",
                "12": "國際貿易環境改善：關稅、貿易協議變動對企業出口與供應鏈的影響。",
                "13": "產業扶持政策：特定產業獲得政府支持，對市場競爭與企業成長的影響。",
                "14": "營收創新高：企業營收成長是否具有可持續性，影響市場評價。",
                "15": "財報超預期：業績表現優於市場預期，影響投資者信心與股價。",
                "16": "財報低於預期：營運結果不如預期，可能導致股價回調與市場信心降低。",
                "17": "毛利率變動：成本控制與定價策略如何影響企業獲利能力。",
                "18": "市場樂觀情緒：投資人預期向好，市場買盤增加，股價可能上漲。",
                "19": "市場恐慌情緒：避險情緒升高，可能引發市場大幅波動或資金流出。",
                "20": "經濟成長趨勢：GDP、消費數據變化對企業營運與市場走勢的影響。",
                "21": "競爭加劇：市場份額爭奪，競爭者動向對公司業務的影響。",
                "22": "競爭對手產品：新產品或技術創新如何影響市場競爭格局。",
                "23": "價格戰影響：產業內降價競爭對企業獲利與市場定位的影響。",
                "24": "市占率變動：企業市場地位提升或下降對股價評價的影響。",
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
                "8": "Internal restructuring and layoff trends: Structural adjustments, layoffs, or reorganizations within the company may raise concerns about stability in the market.",
                "9": "External Benefits or Policy Support: Policy adjustments, economic stimulus plans, and industry subsidies impacting businesses.",
                "10": "Geopolitical Easing: Stabilization of international relations reduces market uncertainty, affecting investor confidence.",
                "11": "Government Subsidies or Tax Incentives: Financial support impacts business operating costs and competitive advantage.",
                "12": "Improvement in International Trade Environment: Changes in tariffs and trade agreements affecting exports and supply chains.",
                "13": "Industry Support Policies: Government support for specific industries impacts market competition and business growth.",
                "14": "Revenue Reaches New Highs: Sustainability of business revenue growth affects market valuation.",
                "15": "Earnings Exceed Expectations: Performance surpassing market expectations impacts investor confidence and stock prices.",
                "16": "Earnings Below Expectations: Weaker-than-expected results may lead to stock price adjustments and reduced market confidence.",
                "17": "Gross Margin Changes: How cost control and pricing strategies affect a company’s profitability.",
                "18": "Optimistic Market Sentiment: Positive investor expectations increase market buying, possibly driving stock prices up.",
                "19": "Market Panic Sentiment: Rising risk aversion may trigger significant market fluctuations or capital outflows.",
                "20": "Economic Growth Trends: GDP and consumer data trends affecting business operations and market movements.",
                "21": "Intensified Competition: Market share battles and competitor actions impacting company performance.",
                "22": "Competitor Product Launches: How new products or technological innovations impact the competitive landscape.",
                "23": "Impact of Price Wars: Industry-wide price reductions affecting corporate profitability and market positioning.",
                "24": "Market Share Changes: The impact of increasing or declining company market share on stock valuation.",
            }
        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
            
        return res_factors_json