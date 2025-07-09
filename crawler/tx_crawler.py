import time
import datetime
import os
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def crawler(start_date, end_date):
    # Download TX data from TAIFEX ------------------------------------------------
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://www.taifex.com.tw/cht/3/dlFutDailyMarketView"
    driver.get(url)
    time.sleep(3)




    start_date_str = start_date.strftime("%Y/%m/%d")
    end_date_str = end_date.strftime("%Y/%m/%d")

    start_date_input = driver.find_element(By.ID, "queryStartDate")
    start_date_input.clear()
    for char in start_date_str:
        start_date_input.send_keys(char)
        time.sleep(0.2)  # 模擬人類輸入的延遲
    print("fill in start date " + start_date_str)

    end_date_input = driver.find_element(By.ID, "queryEndDate")
    end_date_input.clear()
    for char in end_date_str:
        end_date_input.send_keys(char)
        time.sleep(0.2)  # 模擬人類輸入的延遲
    print("fill in end date " + end_date_str)


    while True:
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", end_date_input)
        time.sleep(2)  # 等待下拉選單更新
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.ID, "commodity_idt")).click().pause(1).click().perform()
        time.sleep(2)
        market_type_select = Select(driver.find_element(By.ID, "commodity_idt"))
        options = [option.get_attribute("value") for option in market_type_select.options]
        if "TX" in options:
            market_type_select.select_by_value("TX")
            break  
        else:
            print("TX not found, retrying...")

    download_button = driver.find_element(By.ID, "button4")
    download_button.click()
    time.sleep(5)
    print("資料下載完成！ " + download_path)
    driver.quit()
    

    # 讀取、篩選、合併、儲存資料 ---------------------------------------------------
    download_path = "downloads"
    list_of_files = os.listdir(download_path)
    df = pd.read_csv(download_path + "/" + list_of_files[0], encoding="big5")

    # 修正 df
    old_headers = list(df.columns)
    if len(old_headers) > 1:
        new_headers = old_headers[1:] + ['']
        df.columns = new_headers
    if "交易日期" not in df.columns:
        df.reset_index(inplace=True)
        df.rename(columns={"index": "交易日期"}, inplace=True)
        
    # 篩選
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_filtered = df[df["交易時段"] == "一般"]
    df_filtered["到期月份(週別)"] = pd.to_numeric(df_filtered["到期月份(週別)"], errors='coerce')
    df_filtered = df_filtered.dropna(subset=[df_filtered.columns[1]])
    df_filtered = df_filtered[df_filtered["契約"] == "TX"]
    df_filtered = df_filtered.groupby("交易日期", as_index=False).apply(
        lambda group: group.loc[group["到期月份(週別)"].idxmin()]
    )
    df_filtered.reset_index(drop=True, inplace=True)
    df_filtered = df_filtered[["交易日期", "開盤價", "最高價", "最低價", "收盤價", "成交量"]]
    df_filtered["交易日期"] = df_filtered["交易日期"].str.replace("/", "")
    df_filtered.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

    df_old_data = pd.read_csv("history_data/tw/stock_price/tx.csv")
    df_old_data["Date"] = df_old_data["Date"].astype(str)

    # 如果有重複的日期，則刪除 df_filtered 
    df_filtered = df_filtered[~df_filtered["Date"].isin(df_old_data["Date"])]
    df_filtered.to_csv(f"{os.getcwd()}/history_data/tw/stock_price/tx.csv", index=False, mode="a", header=False)
    print("資料更新完成！")
    
    # 刪除下載的資料
    for file in list_of_files:
        os.remove(os.path.join(download_path, file))

    # 計算技術指標 ---------------------------------------------------------------
    df = pd.read_csv(f"{os.getcwd()}/history_data/tw/stock_price/tx.csv")
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['EMA60'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['MACD'] = df['DIF'].ewm(span=9, adjust=False).mean()

    def calculate_rsi(series, period=14):
        delta = series.diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    df['RSI'] = calculate_rsi(df['Close'])

    low_list = df['Low'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['Low'].expanding().min(), inplace=True)
    high_list = df['High'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['High'].expanding().max(), inplace=True)
    rsv = (df['Close'] - low_list) / (high_list - low_list) * 100

    def historical_volatility(prices, window=10, trading_days=252):
        """
        計算歷史波動率 (Historical Volatility)

        :param prices: 一個包含價格數據的列表或Numpy數組
        :param window: 計算波動率的視窗期 (默認是252天)
        :param trading_days: 年化的交易天數，默認是252
        :return: 年化波動率
        """
        prices = np.asarray(prices)
        # 計算對數收益率
        log_returns = np.log(prices[1:] / prices[:-1])

        # 計算對數收益率的標準差
        std_dev = np.std(log_returns[-window:])

        # 年化波動率
        annualized_volatility = std_dev * np.sqrt(trading_days)
        
        return annualized_volatility

    df['Volatility'] = df['Close'].rolling(window=252).apply(historical_volatility, raw=True)

    # 初始值設定
    df['K'] = 50
    df['D'] = 50
    for i in range(1, len(df)):
        df.loc[df.index[i], 'K'] = (2/3) * df.loc[df.index[i-1], 'K'] + (1/3) * rsv[i]
        df.loc[df.index[i], 'D'] = (2/3) * df.loc[df.index[i-1], 'D'] + (1/3) * df.loc[df.index[i], 'K']

    df.to_csv(f"{os.getcwd()}/history_data/tw/stock_price/tx_tech.csv", encoding='utf-8', index=False)

# # 設定下載日期範圍 (過去一個月) ==============================================
# end_date = datetime.date.today()
# start_date = end_date - datetime.timedelta(days=28)
# # start_date = datetime.date(2025, 2, 1)
# # end_date = datetime.date(2025, 2, 28)
# # =============================================================================
# crawler(start_date, end_date)