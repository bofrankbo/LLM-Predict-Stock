from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import os
import pandas as pd

# # 設定 Chrome WebDriver 選項
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # 無頭模式
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # 設定下載路徑
# download_path = os.path.join(os.getcwd(), "downloads")
# os.makedirs(download_path, exist_ok=True)
# chrome_options.add_experimental_option("prefs", {
#     "download.default_directory": download_path,
#     "download.prompt_for_download": False,
#     "download.directory_upgrade": True,
#     "safebrowsing.enabled": True
# })

# # 使用 webdriver-manager 自動下載對應版本的 ChromeDriver
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # 目標網址 (期交所歷史資料)
# url = "https://www.taifex.com.tw/cht/3/dlFutDailyMarketView"
# driver.get(url)
# time.sleep(3)

# # 設定下載日期範圍 (過去一個月)
# end_date = datetime.date.today()
# start_date = end_date - datetime.timedelta(days=28)

# # 格式化日期
# start_date_str = start_date.strftime("%Y/%m/%d")
# end_date_str = end_date.strftime("%Y/%m/%d")

# # 輸入起始日期
# start_date_input = driver.find_element(By.ID, "queryStartDate")
# start_date_input.clear()
# for char in start_date_str:
#     start_date_input.send_keys(char)
#     time.sleep(0.2)  # 模擬人類輸入的延遲
# print("fill in start date " + start_date_str)

# # 輸入結束日期
# end_date_input = driver.find_element(By.ID, "queryEndDate")
# end_date_input.clear()
# for char in end_date_str:
#     end_date_input.send_keys(char)
#     time.sleep(0.2)  # 模擬人類輸入的延遲
# print("fill in end date " + end_date_str)

# # 觸發 onchange 事件
# driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", end_date_input)
# time.sleep(2)  # 等待下拉選單更新

# # 模擬滑鼠點擊兩次
# actions = ActionChains(driver)
# actions.move_to_element(driver.find_element(By.ID, "commodity_idt")).click().pause(1).click().perform()
# time.sleep(2)

# market_type_select = Select(driver.find_element(By.ID, "commodity_idt"))
# market_type_select.select_by_value("TX")


# # 按下下載按鈕
# download_button = driver.find_element(By.ID, "button4")
# download_button.click()
# time.sleep(5)  # 等待檔案下載

# print("資料下載完成！ " + download_path)

# # 關閉瀏覽器
# driver.quit()

download_path = "C:\_Coding\LLM-Predict-Stock\downloads"
list_of_files = os.listdir(download_path)
df = pd.read_csv(download_path + "\\" + list_of_files[0], encoding="big5")
# print(df.head())

def find_min_expiry(df):
    # 刪除所有空格
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    # 過濾出 "交易時段" 為 "一般" 的資料
    df_filtered = df[df["交易時段"] == "一般"]
    print(df_filtered)
    
    # 轉換 "到期月份(週別)" 為數字以便排序
    df["到期月份(週別)"] = pd.to_numeric(df["到期月份(週別)"], errors='coerce')
    

    
    # 找到最小的 "到期月份(週別)"
    if not df_filtered.empty:
        min_expiry_row = df_filtered.loc[df_filtered["到期月份(週別)"].idxmin()]
        return min_expiry_row.to_frame().T
    else:
        return None

# 執行函數
result = find_min_expiry(df)
print(result)