# 三大法人買賣超資料爬蟲
# python 3.11.7
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import pandas as pd
import os
from io import StringIO
import random

# 設定起始日期和結束日期===========================
start_date = datetime(2024, 5, 31)
end_date = datetime(2024, 7, 24)
# ==============================================

# 設定迭代的步進值，這裡設定為一天
step = timedelta(days=1)

url = 'https://www.taifex.com.tw/cht/3/futContractsDate'
driver = webdriver.Chrome()
driver.get(url)

# 使用 for 迴圈進行迭代
current_date = start_date
while current_date <= end_date:
    d = current_date.strftime('%Y/%m/%d')
    str_d = current_date.strftime('%Y%m%d')
    current_date += step

    # search
    input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div[2]/div[3]/div/div[3]/div/form/fieldset/ul/li[1]/div[2]/input")
    input_search.clear()
    input_search.send_keys(d)
    driver.find_element(By.XPATH, '//*[@id="button"]').click()

    # 找到 tbody 元素
    tbody = driver.find_element(By.TAG_NAME, 'table')
    table_html = tbody.get_attribute('outerHTML')

    # 使用pandas讀取HTML內容並轉換為DataFrame
    df = pd.read_html(StringIO(table_html))[0]

    if df.isin(['查無資料']).any().any():
        print("DataFrame 中包含 '查無資料'")
        continue
    
    path = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin', f'fwbtin_{str_d}.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(path)
    df.to_csv(path, mode='w', encoding='utf-8', index=False)

    time.sleep(random.uniform(1, 3))

# 關閉瀏覽器
driver.quit()
