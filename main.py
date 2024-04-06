import os

import numpy as np
import numpy_financial as npf
import pandas as pd
from google.generativeai.types import HarmBlockThreshold
from google.ai.generativelanguage_v1 import HarmCategory
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI

import secret


def gemini_response(llm, general_prompt, regenerate_count, start_time, end_time, folder_path, sorted_files):
    signal = []
    for index, file_name in enumerate(sorted_files):
        scores = []

        # 檢查日期是否在參考日期之後
        try:
            date_obj = datetime.strptime(file_name, '%Y%m%d')
        except:
            continue
        if date_obj < start_time:
            continue
        elif date_obj > end_time:
            continue

        with open(folder_path + file_name) as f:
            news = f.read()
            prompt = general_prompt + "\n" + news

        for i in range(regenerate_count):
            result = llm.invoke(prompt)
            try:
                scores.append(int(result.content))
            except:
                pass

        if len(scores) == 0:
            score = 0
        else:
            score = sum(scores) / len(scores)

        signal.append([date_obj.strftime('%Y%m%d'), score])
    return signal


def calculate_irr(signal):
    # [日期, 評分, 價格]
    hold = 0  # 持有的股數
    balance_in = []  # 每月投入的資金
    balance_total = 0
    month = 1
    this_month_in = 0
    for item in signal:
        score = float(item[1])
        price = float(item[2])
        if score > 0:
            balance_total += score * 1000  # 買入分數*1000等值的股票
            hold = hold + ((score * 1000) / price)  # 計算持有的股票數

            # 計算每月投入金額
            date_obj = datetime.strptime(item[0], '%Y%m%d')
            if month == date_obj.month:
                this_month_in += score * 1000
            elif month != date_obj.month:
                month = date_obj.month
                this_month_in += score * 1000
                balance_in.append(-this_month_in)
                this_month_in = 0

    balance_in.append(-this_month_in)
    last_price = float(signal[len(signal) - 1][2])

    balance_in.append(hold * last_price)
    # print(balance_in)
    irr = npf.irr(balance_in)
    bnh = hold * last_price / balance_total

    return round(irr, 5), round(bnh, 5)


def mutate_prompt(llm, p_mutate):
    prompt = '產生以下指令的1個變體，同時保留語意：'
    response = llm.invoke(prompt + p_mutate)
    return response.content


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = secret.GEMINI_API_KEY

regenerate_count = 1
prompt_mutate_count = 10

start_time = datetime(2022, 1, 1)
end_time = datetime(2022, 2, 28)

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=1,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    })

p_mutate = '媒體廣泛讚譽其的創新和光明前景，預示著股價將持續上漲。'

stock_ids = ["1101", "2211", "2385", "2542", "2880", "2912", "3023", "3264", "5269", "8027"]

for i in range(prompt_mutate_count):
    p_mutate = mutate_prompt(llm, p_mutate)
    general_prompt = '請依據' + p_mutate + '給這篇文章打一個分數，分數介於-100～100之間，-100是負向，100是最好，0則是無法判斷'

    irrs = []
    bnhs = []
    for stock_id in stock_ids:
        folder_path = "stock_news/" + stock_id + "/" + stock_id + "_news/"
        files = os.listdir(folder_path)
        sorted_files = sorted(files)

        # gemini的回應，回傳帶有買入訊號的list
        signal = gemini_response(llm, general_prompt, regenerate_count, start_time, end_time, folder_path, sorted_files)

        # 加入買入價格
        df = pd.read_csv("price_history/" + stock_id + ".csv", dtype=str)
        price_np = df.to_numpy()
        prices = price_np.tolist()

        signal_2 = []
        for item in signal:
            for price in prices:
                # print(item[0], price[0])
                if item[0] == price[0]:
                    signal_2.append([item[0], item[1], price[1]])

        signal_2_np = np.array(signal_2)
        # 回傳 IRR 以及總額投入
        irr, bnh = calculate_irr(signal_2_np)
        irrs.append(irr)
        bnhs.append(bnh)
        # print("每月內部報酬率", irr)
        # print("總額投入報酬率", bnh)

    # 輸出結果
    write_folder = "evaluate_output/output"
    count = 1
    while True:
        if os.path.exists(write_folder + str(count)):
            count += 1
            continue
        else:
            with open(write_folder + str(count), "a", encoding="UTF-8") as f:
                content = (f'提示：{p_mutate} \n, '
                           f'開始日期{start_time.strftime("%Y%m%d")},'
                           f'結束日期{end_time.strftime("%Y%m%d")}\n')
                for i in range(len(stock_ids)):
                    content += (f'股票代號：{stock_ids[i]}\t'
                                f'每月內部報酬率:{irrs[i]}\t'
                                f'總額投入報酬率:{bnhs[i]}\n')
                f.write(content)
            print("寫入" + write_folder + str(count))
            break
