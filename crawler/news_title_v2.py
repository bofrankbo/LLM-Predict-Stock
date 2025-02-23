import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures
import json
import os
import time
import random
from tqdm import tqdm

# Dow Jones 30 Components (as of Feb 2025) + Additional stocks
data = [
    # Dow Jones Industrial Average Components (alphabetically by symbol)
    ["AMGN", "Amgen", "us"],
    ["AMZN", "Amazon inc.", "us"],
    ["AAPL", "Apple Inc.", "us"],
    ["AXP", "American Express", "us"],
    ["BA", "Boeing", "us"],
    ["BAC", "Bank of America", "us"],
    ["CAT", "Caterpillar", "us"],
    ["CVX", "Chevron", "us"],
    ["CSCO", "Cisco", "us"],
    ["KO", "Coca-Cola", "us"],
    ["CRM", "Salesforce", "us"],
    ["DIS", "Disney", "us"],
    ["DOW", "Dow Inc.", "us"],
    ["GS", "Goldman Sachs", "us"],
    ["HD", "Home Depot", "us"],
    ["HON", "Honeywell", "us"],
    ["IBM", "IBM", "us"],
    ["INTC", "Intel", "us"],
    ["JNJ", "Johnson & Johnson", "us"],
    ["JPM", "JPMorgan Chase", "us"],
    ["MCD", "McDonald's", "us"],
    ["MRK", "Merck", "us"],
    ["MSFT", "Microsoft", "us"],
    ["MMM", "3M", "us"],
    ["NKE", "Nike", "us"],
    ["PG", "Procter & Gamble", "us"],
    ["TRV", "Travelers", "us"],
    ["UNH", "UnitedHealth Group", "us"],
    ["VZ", "Verizon", "us"],
    ["WMT", "Walmart", "us"],
    
    # Additional US stocks
    # ["ADBE", "Adobe", "us"],
    # ["AVGO", "Broadcom", "us"],
    # ["BRK", "Berkshire Hathaway", "us"],
    # ["GOOGL", "Google", "us"],
    # ["META", "Meta Platforms", "us"],
    # ["MRNA", "Moderna", "us"],
    # ["NVDA", "Nvidia", "us"],
    # ["PYPL", "PayPal", "us"],
    # ["TSLA", "Tesla", "us"],
]

# Set date range (one month prior to current date)
end_date = datetime(2024, 12, 31)
start_date = datetime(2023, 6, 1)
# start_date = datetime(2021, 3, 1)

# 隨機 User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
]
def fetch_news(date, stock_name):
    """Fetch news for a specific date and stock"""
    date_str = date.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
    url = f"https://www.google.com/search?q={stock_name}&tbs=cdr:1,cd_min:{date_str},cd_max:{date_str}&tbm=nws&start=0&gl=US&hl=en"
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                return "429", []
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            news = [
                {
                    'headline': elem.find('div', class_='n0jPhd ynAwRc MBeuO nDgy9d').text,
                    'content': elem.find('div', class_='GI74Re nDgy9d').text
                }
                for elem in soup.find_all('div', class_='SoAPf')
                if elem.find('div', class_='n0jPhd ynAwRc MBeuO nDgy9d') and elem.find('div', class_='GI74Re nDgy9d')
            ]
            return date_str, news
            
        except requests.RequestException as e:
            print(f"Error fetching {date_str}: {e}, retrying ({attempt + 1}/3)...")
            time.sleep(600 if attempt < 2 else 0)
    
    return date_str, []

def save_data(path, data):
    """Save data to JSON file"""
    with open(path, "w", encoding="UTF-8") as f:
        json.dump(dict(sorted(data.items())), f, ensure_ascii=False, indent=4)

def crawl_news(start_date, end_date, stock_name, path, existing_data):
    """Crawl Google News headlines"""
    headlines = existing_data.copy()
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    dates_to_fetch = [d for d in dates if d.strftime('%Y%m%d') not in headlines]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_news, date, stock_name): date for date in dates_to_fetch}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc=f"Crawling {stock_name}"):
            date_str, news = future.result()
            
            if date_str == "429":
                save_data(path, headlines)
                print(f"[Rate Limited] Saved progress for {stock_name}, pausing for 10 minutes...")
                time.sleep(600)
                return crawl_news(start_date, end_date, stock_name, path, headlines)
            
            date_key = datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y%m%d')
            headlines[date_key] = news
    
    return headlines

def main():
    for stock in tqdm(data, desc="Overall Progress"):
        stock_code, stock_name, country = stock
        path = os.path.join("history_data", country, "news_title", f"{stock_code}news_title.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Load existing data
        existing_data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="UTF-8") as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Failed to parse {path}")

        # Crawl and save
        headlines = crawl_news(start_date, end_date, stock_name, path, existing_data)
        save_data(path, headlines)

if __name__ == "__main__":
    main()
