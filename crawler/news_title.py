import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures
import json
import os
import time
import random
from tqdm import tqdm

def fetch_news_for_date(date, stock_name):
    date_formatted = date.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
    url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_formatted},cd_max:{date_formatted}&tbm=nws&start=0"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    }

    for _ in range(3):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all('div', class_='n0jPhd ynAwRc MBeuO nDgy9d')
            headlines = [element.text for element in elements]
            return date_formatted, headlines
        except requests.RequestException as e:
            print(f"錯誤獲取新聞 {date_formatted}: {e}")
            time.sleep(random.uniform(1, 3))
    return date_formatted, []

def crawl_google_news_headlines(start_date, end_date, stock_name, existing_data):
    headlines_by_date = existing_data.copy()
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    dates_to_fetch = [date for date in dates if date.strftime('%Y%m%d') not in headlines_by_date]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_news_for_date, date, stock_name): date for date in dates_to_fetch}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"爬取 {stock_name} 的新聞"):
            date_formatted, headlines = future.result()
            date_formatted2 = datetime.strptime(date_formatted, '%m/%d/%Y').strftime('%Y%m%d')
            headlines_by_date[date_formatted2] = headlines

    return headlines_by_date

data = [
    ["2330", "台積電", "31.%"],
    ["2317", "鴻海", "3.3553%"],
    ["2454", "聯發科", "2.462%"],
    ["2382", "廣達", "1.5581%"],
    ["2412", "中華電", "1.4924%"],
    ["2881", "富邦金", "1.3953%"],
    ["2308", "台達電", "1.2916%"],
    ["2882", "國泰金", "1.1493%"],
    ["6505", "台塑化", "1.0671%"],
    ["2891", "中信金", "1.0382%"]
]

# 抓資料存到 json 檔
start_date = datetime(2023, 5, 1)
end_date = datetime(2024, 7, 24)

for idx, stock in enumerate(tqdm(data, desc="總進度")):
    stock_name = stock[1]
    path = os.path.join("history_data", "tw", "news_title", stock[0] + "news_title.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 讀取現有的 JSON 檔案
    if os.path.exists(path):
        with open(path, "r", encoding="UTF-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # 爬取缺少的資料
    headlines = crawl_google_news_headlines(start_date, end_date, stock_name, existing_data)

    # 將資料按照日期排序
    sorted_headlines = dict(sorted(headlines.items()))

    json_content = json.dumps(sorted_headlines, ensure_ascii=False, indent=4)

    with open(path , "w", encoding="UTF-8") as f:
        f.write(json_content)