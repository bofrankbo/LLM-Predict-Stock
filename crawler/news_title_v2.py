import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import random

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def fetch_news(driver, date, stock_name, country):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            date_str = date.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
            url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_str},cd_max:{date_str}&tbm=nws"
            if country == "us":
                url += "&gl=US&hl=en"
            
            driver.get(url)
            
            # 檢查是否出現驗證頁面
            if "sorry/index" in driver.current_url or "g-recaptcha" in driver.page_source:
                print(f"遇到驗證頁面，等待後重試... (第 {retry_count + 1} 次)")
                time.sleep(random.uniform(10))  # 隨機等待 5-10 秒
                driver.refresh()  # 重新整理頁面
                time.sleep(random.uniform(3, 7))  # 再次隨機等待
                retry_count += 1
                
            
                # 等待頁面載入
                time.sleep(random.uniform(2, 5))
                continue
            
            news = [{
                'headline': e.find_element(By.CSS_SELECTOR, 'div.n0jPhd').text,
                'content': e.find_element(By.CSS_SELECTOR, 'div.GI74Re').text
            } for e in driver.find_elements(By.CSS_SELECTOR, 'div.SoAPf')]
            
            return date.strftime('%Y%m%d'), news
            
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(random.uniform(5, 10))
                driver.refresh()
                time.sleep(random.uniform(3, 7))
            else:
                print(f"達到最大重試次數 ({max_retries})，跳過此日期")
                return date.strftime('%Y%m%d'), []

def crawl_news(data, start_date, end_date):
    driver = setup_driver()
    page_count = 0
    
    for stock in data:
        stock_id, stock_name, country = stock
        path = f"history_data/{country}/news_title/{stock_id}news_title.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        existing_data = json.load(open(path, "r", encoding="UTF-8")) if os.path.exists(path) else {}
        
        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        dates_to_fetch = [d for d in dates if d.strftime('%Y%m%d') not in existing_data]
        
        print(f"開始爬取 {stock_name} ({stock_id}) 新聞...")
        for date in dates_to_fetch:
            # 檢查是否需要重新啟動瀏覽器
            if page_count >= 2000:
                if driver:
                    driver.quit()
                driver = setup_driver()
                page_count = 0
                print("重新啟動瀏覽器...")
            
            date_str, headlines = fetch_news(driver, date, stock_name, country)
            existing_data[date_str] = headlines
            print(f"  - {date_str} 新聞已獲取 ({len(headlines)} 則)")
            page_count += 1
        
        existing_data = dict(sorted(existing_data.items(), key=lambda x: x[0])) 
        with open(path, "w", encoding="UTF-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"✅ {stock_name} ({stock_id}) 新聞已更新: {path}\n")
    
    if driver:
        driver.quit()

# 使用示例
data = [
    # ["1560", "中砂", "tw"],
    # ["2330", "台積電", "tw"],
    # ["2317", "鴻海", "tw"],
    # ["2303", "聯電", "tw"],
    # ["3711", "日月光", "tw"],
    # ["2886", "兆豐金", "tw"],
    # ["2886", "兆豐金", "tw"],
    # ["2303", "聯電", "tw"],
    # ["2357", "華碩", "tw"],
    # ["2885", "元大金", "tw"],
    # ["2603", "長榮", "tw"],
    ["2884", "玉山金", "tw"],
    ["1216", "統一集團", "tw"],
    ["3045", "台灣大", "tw"],
    ["2892", "第一金", "tw"],
    ["2880", "華南金", "tw"], #20
]
crawl_news(data, datetime(2022, 1, 1), datetime(2024, 12, 31))
