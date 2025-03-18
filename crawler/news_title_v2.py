import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def fetch_news(driver, date, stock_name, country):
    date_str = date.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
    url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_str},cd_max:{date_str}&tbm=nws"
    if country == "us":
        url += "&gl=US&hl=en"
    driver.get(url)
    news = [{
        'headline': e.find_element(By.CSS_SELECTOR, 'div.n0jPhd').text,
        'content': e.find_element(By.CSS_SELECTOR, 'div.GI74Re').text
    } for e in driver.find_elements(By.CSS_SELECTOR, 'div.SoAPf')]
    return date.strftime('%Y%m%d'), news

def crawl_news(data, start_date, end_date):
    driver = setup_driver()
    for stock in data:
        stock_id, stock_name, country = stock
        path = f"history_data/{country}/news_title/{stock_id}news_title.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        existing_data = json.load(open(path, "r", encoding="UTF-8")) if os.path.exists(path) else {}
        
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        dates_to_fetch = [d for d in dates if d.strftime('%Y%m%d') not in existing_data]
        
        print(f"開始爬取 {stock_name} ({stock_id}) 新聞...")
        for date in dates_to_fetch:
            date_str, headlines = fetch_news(driver, date, stock_name, country)
            existing_data[date_str] = headlines
            print(f"  - {date_str} 新聞已獲取 ({len(headlines)} 則)")
        
        existing_data = dict(sorted(existing_data.items(), key=lambda x: x[0])) 
        with open(path, "w", encoding="UTF-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"✅ {stock_name} ({stock_id}) 新聞已更新: {path}\n")
    driver.quit()

# 使用示例
data = [
    # ["1560", "中砂", "tw"],
    ["2330", "台積電", "tw"],
    ["2317", "鴻海", "tw"],
]
crawl_news(data, datetime(2025, 3, 17), datetime(2025, 3, 17))
