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
import csv

# 設定起始日期和結束日期===========================
start_date = datetime(2024, 8, 30)
end_date = datetime(2024, 9, 2)
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
    print(f"    正在處理 {d} 的資料")

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
        print("DataFrame 中包含[查無資料]，可能不是交易日 => 跳過")
        continue

    path = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin', f'fwbtin_{str_d}.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, mode='w', encoding='utf-8', index=False)
    print("成功取得三大法人資料 => 存檔")
    
    # 取大台買賣超
    path_tx = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw','fwbtin_tx', f'tx_data.csv')
    df_tx = pd.read_csv(path_tx, encoding='utf-8')
    df_last = df_tx.iloc[-1]
    if datetime.strptime(str_d, '%Y%m%d') <= datetime.strptime(str(df_last['日期']), '%Y%m%d'):
        print("tx_data.csv 已有資料 => 跳過")
        continue

    df_fwbtin = df[df[('Unnamed: 1_level_0', 'Unnamed: 1_level_1', '商品 名稱')] == '臺股期貨']

    # 設定新資料框的標題
    columns = ['日期', '自營商多', '自營商空', '自營商多空淨額', '投信多', '投信空', '投信多空淨額', '外資多', '外資空', '外資多空淨額']
    output_df = pd.DataFrame(columns=columns)

    # 使用 .xs 方法進行多層索引的選取
    df_last = pd.DataFrame({
        '日期': str_d,
        '自營商多': df_fwbtin.xs(('未平倉餘額', '多方'), level=[0, 1], axis=1).iloc[0],
        '自營商空': df_fwbtin.xs(('未平倉餘額', '空方'), level=[0, 1], axis=1).iloc[0],
        '自營商多空淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額'), level=[0, 1], axis=1).iloc[0],
        '投信多': df_fwbtin.xs(('未平倉餘額', '多方'), level=[0, 1], axis=1).iloc[1],
        '投信空': df_fwbtin.xs(('未平倉餘額', '空方'), level=[0, 1], axis=1).iloc[1],
        '投信多空淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額'), level=[0, 1], axis=1).iloc[1],
        '外資多': df_fwbtin.xs(('未平倉餘額', '多方'), level=[0, 1], axis=1).iloc[2],
        '外資空': df_fwbtin.xs(('未平倉餘額', '空方'), level=[0, 1], axis=1).iloc[2],
        '外資多空淨額': df_fwbtin.xs(('未平倉餘額', '多空淨額'), level=[0, 1], axis=1).iloc[2]
    })

    row_data = df_last.iloc[0:1].astype(str)

    # 設置 '日期' 為索引
    row_data.set_index('日期', inplace=True)

    # 將 DataFrame 轉換為字串並格式化
    formatted_rows = []
    for index, row in row_data.iterrows():
        formatted_row = [index] + ['{}'.format(x) for x in row]
        formatted_rows.append(formatted_row)

    # 將新資料附加到 CSV 文件後面
    with open(path_tx, mode='a', newline='', encoding='utf-8') as file:
        for row in formatted_rows:
            line = ','.join(row) + '\n'
            file.write(line)
            print("成功寫入 tx_data.csv")

    time.sleep(random.uniform(1, 3))


# 關閉瀏覽器
driver.quit()
