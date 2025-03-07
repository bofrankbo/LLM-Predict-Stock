import os
import json
from datetime import datetime

class UsableExpGenerator:
    '''
        由前8個Factor篩選後由GPT-4o產生新的Factor
    '''
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/UsableExp.json"    # 輸出 JSON 檔案
        
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
                "9": "資金流動與外資動向：外資買超或賣超、內資是否進場，影響市場流動性與股價變化。",
                "10": "貨幣政策與利率變動：央行升息或降息、貨幣政策方向會影響資金成本與市場估值。",
                "11": "產業景氣循環：產業是否進入景氣高峰或低谷，例如半導體、航運、原物料等行業的週期性波動。",
                "12": "企業併購與合作：大型企業併購案、策略聯盟、合作協議可能提升市場對企業未來發展的期待。",
                "13": "法律與監管風險：新法規、監管政策變更，可能影響企業營運與市場信心。",
                "14": "市場黑天鵝事件：突發性重大事件，如戰爭、疫情、重大公司醜聞等，可能造成市場劇烈波動。",
                "15": "ESG（環境、社會、治理）影響：企業的永續發展政策、環境問題或社會責任履行，影響投資者信心。",
                "16": "股利政策與回購計畫：企業是否發放股利或進行庫藏股回購，影響股價穩定性與投資者吸引力。"
            }
        elif country == 'us':
            print('us is not available')
            # res_factors_json = {
            #     "1": "External benefits or policy support: Geopolitical easing, government support, or improvement in external environments.",
            #     "2": "Revenue or financial performance: Record-high revenue, exceeding expectations, or falling short of expectations.",
            #     "3": "Market sentiment or economic impact: Optimistic or panicked market sentiment, overall economic slowdown, or improvement.",
            #     "4": "Competitive pressure: Intensified industry competition, exceptional performance by peers, or heightened competition within the industry affecting market share and company valuation.",
            #     "5": "Product innovation and new technology launches: Launching new products or technologies that attract investor attention and boost market confidence.",
            #     "6": "Market sentiment and analyst predictions: Investor sentiment and optimistic analyst forecasts have a significant impact on stock price fluctuations.",
            #     "7": "Supply chain and production challenges: Changes or delays in the supply chain during production processes may negatively impact the company's stock price.",
            #     "8": "Internal restructuring and layoff trends: Structural adjustments, layoffs, or reorganizations within the company may raise concerns about stability in the market."
            # }

        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
            
        return res_factors_json