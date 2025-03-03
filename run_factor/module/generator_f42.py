import os
import json
from datetime import datetime

class GeneratorF42:
    def __init__(self, env, price_his):
        self.env = env
        self.price_his = price_his
        self.path_factors = f"out_stock/Factors/F42/{env['stock_id']}/factors.json"    # 輸出 JSON 檔案
        
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
                "1": "外部利多或政策支持：政策調整、經濟刺激方案、產業補助對企業的影響。",
                "2": "地緣政治緩和：國際關係趨穩，降低市場不確定性，影響投資信心。",
                "3": "政府補貼或稅收優惠：財政支持如何影響企業經營成本與競爭優勢。",
                "4": "國際貿易環境改善：關稅、貿易協議變動對企業出口與供應鏈的影響。",
                "5": "產業扶持政策：特定產業獲得政府支持，對市場競爭與企業成長的影響。",
                "6": "營收創新高：企業營收成長是否具有可持續性，影響市場評價。",
                "7": "財報超預期：業績表現優於市場預期，影響投資者信心與股價。",
                "8": "財報低於預期：營運結果不如預期，可能導致股價回調與市場信心降低。",
                "9": "毛利率變動：成本控制與定價策略如何影響企業獲利能力。",
                "10": "市場樂觀情緒：投資人預期向好，市場買盤增加，股價可能上漲。",
                "11": "市場恐慌情緒：避險情緒升高，可能引發市場大幅波動或資金流出。",
                "12": "經濟成長趨勢：GDP、消費數據變化對企業營運與市場走勢的影響。",
                "13": "競爭加劇：市場份額爭奪，競爭者動向對公司業務的影響。",
                "14": "競爭對手產品：新產品或技術創新如何影響市場競爭格局。",
                "15": "價格戰影響：產業內降價競爭對企業獲利與市場定位的影響。",
                "16": "市占率變動：企業市場地位提升或下降對股價評價的影響。",
                "17": "技術創新突破：研發進展如何影響企業長期競爭力與市場預期。",
                "18": "新產品發布：產品能否獲得市場關注，對業績與股價的影響。",
                "19": "研發投入變動：短期成本與長期回報的平衡，如何影響企業財務。",
                "20": "專利與技術優勢：企業的技術壁壘與競爭力提升如何影響股價。",
                "21": "投行上調評級：分析機構看好企業前景，市場可能做出正面反應。",
                "22": "投行下調評級：分析師調降預測，市場可能擔憂企業未來成長。",
                "23": "分析師上修預測：市場預期調整，影響投資決策與市場趨勢。",
                "24": "分析師風險警告：未來可能面臨的挑戰，市場情緒可能受影響。",
                "25": "供應鏈問題：零組件短缺或供應鏈變動如何影響企業生產。",
                "26": "原物料成本波動：原油、金屬、農產品價格變動對企業成本的影響。",
                "27": "物流與運輸挑戰：全球供應鏈中斷或延遲如何影響出貨與營收。",
                "28": "供應鏈轉移：生產基地轉移對企業成本、效率與風險的影響。",
                "29": "高層變動：管理層更替如何影響市場信心與企業未來戰略。",
                "30": "裁員與組織調整：人事變動是否反映企業營運壓力或策略調整。",
                "31": "內部業務重組：併購、分拆或策略轉向對企業長期發展的影響。",
                "32": "成本削減計畫：縮減開支如何影響企業財務表現與市場預期。",
                "33": "財務槓桿變動：企業資本結構調整對風險與回報的影響。",
                "34": "債務風險變動：負債水平上升或下降如何影響企業評級與資金成本。",
                "35": "企業併購或合併：戰略性收購或合併如何影響市場競爭力與財報。",
                "36": "股東回報策略：股息政策、股票回購對股價與股東信心的影響。",
                "37": "法律與監管變動：政策變更如何影響企業合規成本與市場競爭力。",
                "38": "市場熱點與資金流向：熱門產業或板塊吸引資金，影響整體市場動向。",
                "39": "社會與環境責任：ESG（環境、社會、公司治理）趨勢如何影響企業評價。",
                "40": "品牌與公眾信任：企業形象、消費者信任對業務發展與市場價值的影響。",
                "41": "意外事件影響：黑天鵝事件、自然災害或企業醜聞對市場的衝擊。",
                "42": "數位轉型與科技應用：企業如何運用數據、AI、雲端技術提升競爭力。"
            }
        elif country == 'us':
            res_factors_json = {
                "1": "External Benefits or Policy Support: Policy adjustments, economic stimulus plans, and industry subsidies impacting businesses.",
                "2": "Geopolitical Easing: Stabilization of international relations reduces market uncertainty, affecting investor confidence.",
                "3": "Government Subsidies or Tax Incentives: Financial support impacts business operating costs and competitive advantage.",
                "4": "Improvement in International Trade Environment: Changes in tariffs and trade agreements affecting exports and supply chains.",
                "5": "Industry Support Policies: Government support for specific industries impacts market competition and business growth.",
                "6": "Revenue Reaches New Highs: Sustainability of business revenue growth affects market valuation.",
                "7": "Earnings Exceed Expectations: Performance surpassing market expectations impacts investor confidence and stock prices.",
                "8": "Earnings Below Expectations: Weaker-than-expected results may lead to stock price adjustments and reduced market confidence.",
                "9": "Gross Margin Changes: How cost control and pricing strategies affect a company’s profitability.",
                "10": "Optimistic Market Sentiment: Positive investor expectations increase market buying, possibly driving stock prices up.",
                "11": "Market Panic Sentiment: Rising risk aversion may trigger significant market fluctuations or capital outflows.",
                "12": "Economic Growth Trends: GDP and consumer data trends affecting business operations and market movements.",
                "13": "Intensified Competition: Market share battles and competitor actions impacting company performance.",
                "14": "Competitor Product Launches: How new products or technological innovations impact the competitive landscape.",
                "15": "Impact of Price Wars: Industry-wide price reductions affecting corporate profitability and market positioning.",
                "16": "Market Share Changes: The impact of increasing or declining company market share on stock valuation.",
                "17": "Technological Innovation Breakthroughs: How R&D progress affects long-term competitiveness and market expectations.",
                "18": "New Product Releases: The market reception of new products and their impact on revenue and stock prices.",
                "19": "Changes in R&D Investment: The balance between short-term costs and long-term returns affecting corporate finances.",
                "20": "Patent and Technological Advantage: How a company’s technological barriers and competitiveness impact stock value.",
                "21": "Investment Banks Upgrade Ratings: Analysts' optimistic outlooks leading to positive market reactions.",
                "22": "Investment Banks Downgrade Ratings: Analysts lowering projections may raise concerns about future business growth.",
                "23": "Analyst Forecast Upgrades: Market expectations adjustments affecting investment decisions and trends.",
                "24": "Analyst Risk Warnings: Potential future challenges may impact market sentiment.",
                "25": "Supply Chain Issues: Component shortages or supply chain shifts affecting company production.",
                "26": "Raw Material Cost Fluctuations: Changes in oil, metal, and agricultural product prices affecting company expenses.",
                "27": "Logistics and Transportation Challenges: Global supply chain disruptions or delays impacting shipments and revenue.",
                "28": "Supply Chain Relocation: The impact of shifting production bases on costs, efficiency, and risks.",
                "29": "Executive Changes: How leadership transitions impact market confidence and corporate strategies.",
                "30": "Layoffs and Organizational Adjustments: Workforce changes reflecting operational pressures or strategic realignments.",
                "31": "Internal Business Restructuring: The impact of mergers, spinoffs, or strategy shifts on long-term business development.",
                "32": "Cost Reduction Plans: How expense-cutting measures impact financial performance and market expectations.",
                "33": "Changes in Financial Leverage: Corporate capital structure adjustments affecting risk and returns.",
                "34": "Debt Risk Variations: Rising or falling debt levels affecting credit ratings and financing costs.",
                "35": "Mergers and Acquisitions: The impact of strategic acquisitions or mergers on market competitiveness and financials.",
                "36": "Shareholder Return Strategies: The impact of dividend policies and share buybacks on stock prices and investor confidence.",
                "37": "Legal and Regulatory Changes: How policy shifts affect compliance costs and market competitiveness.",
                "38": "Market Hotspots and Capital Flow Trends: The influence of popular industries or sectors attracting investment.",
                "39": "Social and Environmental Responsibility: How ESG (Environmental, Social, and Governance) trends impact corporate valuation.",
                "40": "Brand and Public Trust: The impact of corporate reputation and consumer trust on business growth and market value.",
                "41": "Impact of Unexpected Events: The effects of black swan events, natural disasters, or corporate scandals on the market.",
                "42": "Digital Transformation and Technology Adoption: How companies use data, AI, and cloud technology to enhance competitiveness."
            }

        with open(self.path_factors, 'w', encoding='utf-8') as f:
            json.dump(res_factors_json, f, ensure_ascii=False, indent=4)
            
        return res_factors_json