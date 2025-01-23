import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures
import json
import os
import time
import random
from tqdm import tqdm

##################################################
# 設定爬取的日期範圍和股票清單

start_date = datetime(2023, 4, 1)
end_date = datetime(2024, 12, 31)

data = [
    ["2330", "台積電", "tw"],
    ["2317", "鴻海", "tw"],
    ["2454", "聯發科", "tw"],
    ["2382", "廣達", "tw"],
    ["3231", "緯創", "tw"],
    ["2207", "和泰車", "tw"],
    ["2881", "富邦金", "tw"],
    ["2412", "中華電", "tw"],
    ["3045", "台灣大", "tw"],
    ["6505", "台塑化", "tw"],
    ["2603", "長榮", "tw"],
    ["6214", "精誠", "tw"],
    ["2379", "瑞昱", "tw"],
    ["3661", "世芯", "tw"],
    ["2408", "南亞科", "tw"],
    ["2357", "華碩", "tw"],
    ["2345", "智邦", "tw"],
    
    ["AAPL", "Apple Inc.", "us"],
    ["GOOGL", "Google", "us"],
    ["MSFT", "Microsoft", "us"],
    ["AMZN", "Amazon inc.", "us"],
    ["TSLA", "Tesla", "us"],
    ["NVDA", "Nvidia", "us"],
    ["META", "Meta Platforms", "us"],
    ["BRK", "Berkshire Hathaway", "us"],
    ["JPM", "JPMorgan Chase", "us"],
    ["WMT", "Walmart", "us"],
    ["UNH", "UnitedHealth Group", "us"],
    # ["DIS", "Disney", "us"],
    # ["BAC", "Bank of America", "us"],
    # ["AVGO", "Broadcom", "us"],
    # ["PYPL", "PayPal", "us"],
    # ["ADBE", "Adobe", "us"],
]

##################################################


def fetch_news_for_date(date, stock_name, country):
    date_formatted = date.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
    if country == "tw":
        url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_formatted},cd_max:{date_formatted}&tbm=nws&start=0"
    elif country == "us":
        url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_formatted},cd_max:{date_formatted}&tbm=nws&start=0&gl=US&hl=en"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }

    for _ in range(3):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all('div', class_='SoAPf')
            news = []
            for element in elements:
                headline = element.find(
                    'div', class_='n0jPhd ynAwRc MBeuO nDgy9d')
                content = element.find('div', class_='GI74Re nDgy9d')
                if headline and content:
                    news.append({
                        'headline': headline.text,
                        'content': content.text
                    })
            return date_formatted, news
        except requests.RequestException as e:
            print(f"錯誤獲取新聞 {date_formatted}: {e}")
            time.sleep(random.uniform(1, 3))
    return date_formatted, []


def crawl_google_news_headlines(start_date, end_date, stock_name, country, existing_data):
    headlines_by_date = existing_data.copy()
    dates = [start_date + timedelta(days=i)
             for i in range((end_date - start_date).days + 1)]
    dates_to_fetch = [date for date in dates if date.strftime(
        '%Y%m%d') not in headlines_by_date]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(
            fetch_news_for_date, date, stock_name, country): date for date in dates_to_fetch}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"爬取 {stock_name} 的新聞"):
            date_formatted, headlines = future.result()
            date_formatted2 = datetime.strptime(
                date_formatted, '%m/%d/%Y').strftime('%Y%m%d')
            headlines_by_date[date_formatted2] = headlines

    return headlines_by_date


for idx, stock in enumerate(tqdm(data, desc="總進度")):
    stock_name = stock[1]
    country = stock[2]
    path = os.path.join("history_data", country, "news_title", stock[0] + "news_title.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 讀取現有的 JSON 檔案
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="UTF-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            print(f"無法解析 {path} 的 JSON 檔案")
    else:
        existing_data = {}

    # 爬取缺少的資料
    headlines = crawl_google_news_headlines(start_date, end_date, stock_name, country, existing_data)

    # 將資料按照日期排序
    sorted_headlines = dict(sorted(headlines.items()))

    json_content = json.dumps(sorted_headlines, ensure_ascii=False, indent=4)

    with open(path, "w", encoding="UTF-8") as f:
        f.write(json_content)
