import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Generator_Index:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/{env['path_folder']}/{env['stock_id']}/factors.json"    # 輸出 JSON 檔案
        
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
                "1": "企業創新策略：企業創新的核心主題，涵蓋所有驅動企業增長和競爭力提升的策略。",
                "2": "滿足客戶需求：企業創新的首要驅動力，能否滿足客戶需求直接影響創新成敗。",
                "3": "吸引投資者關注：投資者的關注和信心能為企業提供必要的資金和支持，是創新成功的重要標誌。",
                "4": "市場需求與趨勢：市場需求的變化和行業趨勢是影響企業股票表現的關鍵因素，企業需適應並預測市場變化。",
                "5": "財務表現：穩定且增長的收入、利潤和現金流是吸引投資者的主要因素，能增加投資者信心，推動股價上漲。",
                "6": "技術進步與研發投入：持續的技術創新和研發投入能提高企業競爭力和市場地位，促進企業長期增長。",
                "7": "經營效率：有效的經營管理能提高企業盈利能力，進而提升股票價值。",
                "8": "品牌聲譽與市場認可度：良好的品牌聲譽和市場認可度能增加企業產品的市場需求，促進銷售增長。",
                "9": "政策與法規支持：政府政策和法規對行業的支持或限制會直接影響企業的發展前景和市場表現。",
                "10": "競爭優勢與市場份額：企業在市場中的競爭優勢和市場份額的提升能增強其市場地位，吸引更多投資者。",
                "11": "全球化與國際市場拓展：進入國際市場並擴展全球業務能增加企業的市場規模和收入來源。",
                "12": "風險管理與應對能力：有效的風險管理策略和應對能力能降低企業運營風險，提高投資者信心。",
                "13": "人才管理與員工激勵：擁有高素質的人才和有效的激勵機制能提升企業創新能力和生產效率。",
                "14": "合作夥伴關係：與其他企業建立戰略合作夥伴關係能共享資源和技術，提升市場競爭力。",
                "15": "市場營銷與品牌推廣：有效的市場營銷和品牌推廣策略能提高企業知名度和市場需求。",
                "16": "客戶服務與滿意度：高品質的客戶服務和較高的客戶滿意度能提高客戶忠誠度和口碑。",
                "17": "供應鏈管理：高效的供應鏈管理能確保產品質量和交付效率，降低成本。",
                "18": "產品多樣化與創新：不斷推出創新產品和服務能滿足不同市場需求，提升企業競爭力。",
                "19": "環保與可持續發展：採用環保和可持續發展策略能提高企業形象，吸引關注可持續投資的投資者。",
                "20": "數位轉型與科技應用：積極進行數位轉型和應用新技術能提高運營效率和市場響應速度。",
                "21": "競爭對手分析與市場擴展：深入分析競爭對手的策略和行動，制定有效的市場擴展和新市場進入策略。",
                "22": "資本結構、財務穩定性與資金籌措：健康的資本結構和財務穩定性以及有效的資金籌措能增強企業的抗風險能力和持續發展能力。",
                "23": "客戶數據分析：利用大數據和數據分析技術深入了解客戶需求，提升產品和服務的針對性。",
                "24": "知識產權保護：有效保護企業的知識產權能防止競爭對手抄襲，提高創新成果的市場價值。",
                "25": "企業文化與價值觀：建立積極向上的企業文化和價值觀能吸引優秀人才，提升企業凝聚力和創新力。",
                "26": "股東回報與分紅政策：穩定的股東回報和合理的分紅政策能吸引長期投資者。",
                "27": "社會責任與公益活動：積極參與社會責任和公益活動能提升企業形象，獲得更多社會支持。",
                "28": "成本控制: 有效的成本控制能提高企業獲利能力。"
            }
        elif country == 'us':
            res_factors_json = {
                "1": "Corporate Innovation Strategy: The core theme of corporate innovation, covering all strategies that drive business growth and enhance competitiveness.",
                "2": "Meeting Customer Needs: The primary driver of corporate innovation; the ability to meet customer needs directly impacts the success of innovation.",
                "3": "Attracting Investor Attention: Investor interest and confidence provide necessary funding and support, serving as a key indicator of innovation success.",
                "4": "Market Demand and Trends: Changes in market demand and industry trends are crucial factors affecting stock performance; companies must adapt and anticipate market changes.",
                "5": "Financial Performance: Stable and growing revenue, profits, and cash flow are major factors attracting investors, boosting investor confidence and driving stock prices up.",
                "6": "Technological Advancement and R&D Investment: Continuous technological innovation and investment in R&D enhance competitiveness and market position, fostering long-term growth.",
                "7": "Operational Efficiency: Effective management improves profitability, thereby increasing stock value.",
                "8": "Brand Reputation and Market Recognition: A strong brand reputation and market recognition boost product demand, driving sales growth.",
                "9": "Policy and Regulatory Support: Government policies and regulations can either support or restrict industry development, directly impacting business prospects and market performance.",
                "10": "Competitive Advantage and Market Share: Strengthening competitive advantages and expanding market share enhance market position and attract more investors.",
                "11": "Globalization and International Expansion: Entering international markets and expanding global operations increase market size and revenue sources.",
                "12": "Risk Management and Response Capabilities: Effective risk management strategies and response capabilities reduce operational risks and enhance investor confidence.",
                "13": "Talent Management and Employee Motivation: High-quality talent and effective incentive mechanisms enhance innovation and productivity.",
                "14": "Partnerships and Strategic Alliances: Establishing strategic partnerships allows resource and technology sharing, improving market competitiveness.",
                "15": "Marketing and Brand Promotion: Effective marketing and branding strategies enhance brand awareness and market demand.",
                "16": "Customer Service and Satisfaction: High-quality customer service and high satisfaction levels increase customer loyalty and reputation.",
                "17": "Supply Chain Management: Efficient supply chain management ensures product quality, delivery efficiency, and cost reduction.",
                "18": "Product Diversification and Innovation: Continuously introducing innovative products and services meets diverse market needs and strengthens competitiveness.",
                "19": "Environmental Protection and Sustainability: Adopting environmentally friendly and sustainable strategies enhances corporate image and attracts ESG-focused investors.",
                "20": "Digital Transformation and Technology Adoption: Actively pursuing digital transformation and adopting new technologies improves operational efficiency and market responsiveness.",
                "21": "Competitor Analysis and Market Expansion: In-depth analysis of competitors' strategies and actions to formulate effective market expansion and entry strategies.",
                "22": "Capital Structure, Financial Stability, and Fundraising: A healthy capital structure, financial stability, and effective fundraising enhance risk resistance and long-term sustainability.",
                "23": "Customer Data Analytics: Utilizing big data and analytics to gain deeper insights into customer needs, improving product and service precision.",
                "24": "Intellectual Property Protection: Effective protection of intellectual property prevents competitors from copying innovations, increasing market value.",
                "25": "Corporate Culture and Values: A strong corporate culture and values attract top talent, enhancing cohesion and innovation.",
                "26": "Shareholder Returns and Dividend Policy: Stable shareholder returns and reasonable dividend policies attract long-term investors.",
                "27": "Corporate Social Responsibility and Philanthropy: Active participation in CSR and philanthropic activities enhances corporate image and social support.",
                "28": "Cost Control: Effective cost control improves profitability."
                }


        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
            
        return res_factors_json
    
    def get_news(self):
        stocks = self.env['components']
        
        # set the news start and end date
        # st,et 在 start_date, start_date 中約 3/4 之間
        start_date = datetime.strptime(self.env['start_date'], '%Y%m%d')
        end_date = datetime.strptime(self.env['end_date'], '%Y%m%d')
        st = start_date + timedelta(days=(end_date - start_date).days * 3 / 4 - 15)
        et = start_date + timedelta(days=(end_date - start_date).days * 3 / 4)

        df_price_his = self.price_his.copy()
        df_price_his['Date'] = pd.to_datetime(self.price_his['Date'], format='%Y%m%d')
        df_price_his = df_price_his[(st <= df_price_his['Date']) & (self.price_his['Date'] <= et)]
        
        news_rise = ''
        news_fall = ''
        for index, row in df_price_his.iterrows():
            news_daily = ""
            for stock in stocks:
                stock_id = stock[0]
                stock_name = stock[1]
                country = stock[2]
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

        print("Those news will make stock price rise: ", news_rise)
        print()
        print("Those news will make stock price fall: ", news_fall)
        
        return news_rise, news_fall