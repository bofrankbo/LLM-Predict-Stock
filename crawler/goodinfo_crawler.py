from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 設定Chrome WebDriver選項
chrome_options = Options()
chrome_options.add_argument("--headless")  # 無頭模式，不開啟瀏覽器視窗
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 指定ChromeDriver路徑 (請確認對應版本)
service = Service("chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 目標網址 (台積電2330)
url = "https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID=2330"
driver.get(url)

# 等待頁面加載
time.sleep(3)

# 爬取股票名稱與股價
stock_name = driver.find_element(By.XPATH, "//td[@style='padding-top:2px;padding-bottom:0px;']").text.strip()
current_price = driver.find_element(By.XPATH, "//td[@style='padding:0 2px 5px 20px;width:10px;']").text.strip()

print(f'股票名稱: {stock_name}')
print(f'目前股價: {current_price}')

# 關閉瀏覽器
driver.quit()
