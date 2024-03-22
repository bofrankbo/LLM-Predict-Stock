from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

url = 'https://www.cnyes.com/search/news?keyword=%E9%88%A6%E6%98%87'
driver = webdriver.Chrome()
driver.get(url)

# 找到 class 屬性包含 "jsx-1986041679" 和 "news" 的所有 <a> 元素
element = driver.find_elements(By.XPATH, '//a[contains(@class, "jsx-1986041679") and contains(@class, "news")]')

for e in element:
    # 獲取該元素的 href 屬性
    href = e.get_attribute('href')

    print("目標元素的網址:", href)

driver.quit()
