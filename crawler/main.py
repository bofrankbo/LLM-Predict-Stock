from datetime import datetime

from fwbtin import crawler as fwbtin_crawler
from tx_crawler import crawler as tx_crawler
from news_title import crawler as news_crawler

# stock list
data = [
    # ["2330", "台積電", "tw"],
    # ["2454", "聯發科", "tw"],
    # ["2317", "鴻海", "tw" ],
    # ["2881", "富邦金", "tw" ],
    # ["2308", "台達電", "tw" ],
    # ["2882", "國泰金", "tw" ],
    # ["2412", "中華電", "tw" ],
    # ["2382", "廣達", "tw" ],
    # ["2891", "中信金", "tw" ],
    ["3711", "日月光投控", "tw"], #10
    # # ["2886", "兆豐金", "tw" ],
    # # ["2303", "聯電", "tw" ],
    # ["2357", "華碩", "tw" ],   
    # # ["2885", "元大金", "tw" ],  # 15
    # ["2603", "長榮", "tw" ],     
    # ["2884", "玉山金", "tw" ],
    # # ["1216", "統一", "tw" ],
    # ["3045", "台灣大", "tw" ],
    # ["2892", "第一金", "tw" ],
    # # ["2880", "華南金", "tw" ],   #20
    
    # ["2002", "中鋼", "tw" ],
    # ["2345", "智邦", "tw" ],
    # ["5880", "合庫金", "tw" ],
    # ["6505", "台塑化", "tw" ],
    # ["6669", "緯穎", "tw" ],
    # ["3008", "大立光", "tw" ],
    # ["2395", "研華", "tw" ],
    # ["2207", "和泰車", "tw" ],
    # ["3034", "聯詠", "tw" ],
    # ["3231", "緯創", "tw" ]      #30
    
    # # old us
    # ["AAPL", "Apple Inc.", "us"],
    # ["MSFT", "Microsoft", "us"],    
    # ["NVDA", "Nvidia", "us"],
    # ["AMZN", "Amazon inc.", "us"],
    # ["JPM", "JPMorgan Chase", "us"],
    # ["BA", "Boeing", "us"],
    # ["UNH", "UnitedHealth Group", "us"],
    # ["CSCO", "Cisco", "us"],
    # ["CVX", "Chevron", "us"],
    # ["PG", "Procter & Gamble", "us"],
    # ["DIS", "Disney", "us"],          # 10
    # ["META", "Meta Platforms", "us"],
    # ["GOOGL", "Google", "us"],
    # ["TSLA", "Tesla", "us"],
    # ["AVGO", "Broadcom", "us"],
    # ["BRK", "Berkshire Hathaway", "us"],
    # ["MRNA", "Moderna", "us"],
    # ["PYPL", "PayPal", "us"],
    # ["BAC", "Bank of America", "us"],
    # ["HD", "Home Depot", "us"],
    # ["WMT", "Walmart", "us"],
    # ["INTC", "Intel", "us"],
    # ["ADBE", "Adobe", "us"],          #20
    
    # # DJIA 
    # ["AAPL", "Apple Inc.", "us"],
    # ["AMGN", "Amgen", "us"],
    # ["AMZN", "Amazon inc.", "us"],
    # ["AXP", "American Express", "us"],
    # ["BA", "Boeing", "us"],
    # ["CSCO", "Cisco", "us"],
    # ["CVX", "Chevron", "us"],
    # ["KO", "Coca-Cola", "us"],
    # ["CAT", "Caterpillar Inc.", "us"],
    # ["CRM", "Salesforce", "us"],    # 10
    # ["DIS", "Disney", "us"],
    # ["GS", "Goldman Sachs", "us"],
    # ["HD", "Home Depot", "us"],
    # ["HON", "Honeywell", "us"],
    # ["IBM", "IBM", "us"],
    # ["JNJ", "Johnson & Johnson", "us"],
    # ["JPM", "JPMorgan Chase", "us"],
    # ["MCD", "McDonald's", "us"],
    # ["MRK", "Merck", "us"],
    # ["MSFT", "Microsoft", "us"],    # 20
    # ["MMM", "3M", "us"],
    # ["NKE", "Nike", "us"],
    # ["NVDA", "Nvidia", "us"],
    # ["PG", "Procter & Gamble", "us"],
    # ["SHW", "Sherwin-Williams", "us"],
    # ["TRV", "Travelers", "us"],
    # ["UNH", "UnitedHealth Group", "us"],
    # ["VZ", "Verizon", "us"],
    # ["V", "Visa", "us"],
    # ["WMT", "Walmart", "us"],   # 30
    
    # Removed from DJIA in past 3 years
    # ["INTC", "Intel", "us"],
    # ["DOW", "Dow Inc.", "us"],
    # ["WBA", "Walgreens Boots Alliance", "us"],
    
    # Not in DJIA
    # ["ADBE", "Adobe", "us"],
    # ["AVGO", "Broadcom", "us"],
    # ["BRK", "Berkshire Hathaway", "us"],
    # ["GOOGL", "Google", "us"],
    # ["META", "Meta Platforms", "us"],
    # ["MRNA", "Moderna", "us"],
    # ["NVDA", "Nvidia", "us"],
    # ["PYPL", "PayPal", "us"],
    # ["TSLA", "Tesla", "us"],
    # ["BAC", "Bank of America", "us"],
]

# end_date = datetime.date.today()
# start_date = end_date - datetime.timedelta(days=28)
start_date = datetime(2024, 12, 1)
end_date = datetime(2024, 12, 31)

# print(f"日期範圍: {start_date} ~ {end_date}")
# print("三大法人")
# fwbtin_crawler(start_date, end_date)

# print("台指期")
# tx_crawler(start_date, end_date)

print("新聞, 需要人工解機器人")
news_crawler(data, start_date, end_date)
