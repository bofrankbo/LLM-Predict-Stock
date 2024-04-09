import os

import numpy as np
import numpy_financial as npf
import pandas as pd
from google.generativeai.types import HarmBlockThreshold
from google.ai.generativelanguage_v1 import HarmCategory
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI

import secret


def gemini_response(model, instruction, count):
    scores = []

    for i in range(count):

        try:
            result = model.invoke(instruction)
            scores.append(int(result.content))
        except:
            pass

    if len(scores) == 0:
        score = 0
    else:
        score = sum(scores) / len(scores)

    return [date_obj.strftime('%Y%m%d'), score]  # [時間, 分數]


def calculate_irr(signal, threshold):
    # [日期, 評分, 價格]
    hold = 0  # 持有的股數
    balance_in = []  # 每月投入的資金
    balance_total = 0
    month = 1
    this_month_in = 0
    for item in signal:
        score = float(item[1])
        price = float(item[2])
        if score > threshold:
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
    if balance_total > 0:
        bnh = last_price / float(signal[0][2])
    else:
        bnh = 0

    return round(irr, 5), round(bnh, 5)


def mutate_prompt(llm, p_mutate):
    prompt = '產生以下指令的1個變體，同時保留語意：'
    response = llm.invoke(prompt + p_mutate)
    return response.content


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = secret.GEMINI_API_KEY

regenerate_count = 3
prompt_mutate_count = 50

start_time = datetime(2023, 1, 1)
end_time = datetime(2023, 12, 31)

# stock_ids = ["1101", "2211", "2385", "2542", "2880", "2912", "3023", "3264", "5269", "8027"]
stock_ids = ["1101", "2211", "2385", "2542", "2880"]

llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=1,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    })

p_mutate = '深入的媒體報導突出了公司的創新突破和行業領先地位，預測其股票價值將繼續穩步攀升，這表明對其未來表現持樂觀態度。'
irr_ = 0.04

for i in range(prompt_mutate_count):
    # 變異
    p_mutate_2 = mutate_prompt(llm, p_mutate)
    general_prompt = '請依據' + p_mutate_2 + '給這篇文章打一個分數，分數介於-100～100之間，-100是負向，100是最好，0則是無法判斷'

    irrs = []
    bnhs = []
    raw_data = []
    for stock_id in stock_ids:
        print(f'變異{i + 1}次\t執行{stock_id}')
        folder_path = "stock_news/" + stock_id + "/" + stock_id + "_news/"
        files = os.listdir(folder_path)
        sorted_files = sorted(files)

        # 載入買進價格
        df = pd.read_csv("price_history/" + stock_id + ".csv", dtype=str)
        price_np = df.to_numpy()
        prices = price_np.tolist()  # [時間,價格]

        signal_2 = []

        for price in prices:
            # 檢查日期是否在參考日期之後
            try:
                date_obj = datetime.strptime(price[0], '%Y%m%d')
            except:
                continue

            if not (start_time <= date_obj <= end_time):
                continue

            for index, file_name in enumerate(sorted_files):
                if file_name == price[0]:
                    with open(folder_path + file_name) as f:
                        news = f.read()
                        prompt = general_prompt + "\n" + news
                        # gemini的回應，回傳帶有買入訊號的list
                        signal = gemini_response(llm, prompt, regenerate_count)
                        # print(price)
                        # print(signal)
                        signal_2.append([price[0], signal[1], price[1]])

        signal_2_np = np.array(signal_2)
        # 回傳 IRR 以及總額投入
        irr, bnh = calculate_irr(signal_2_np, 0)
        irrs.append(irr)
        bnhs.append(bnh)
        raw_data.append(signal_2_np.tolist())
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
                content = (f'提示：{p_mutate_2} mutate from {p_mutate}\n'
                           f'開始日期 {start_time.strftime("%Y%m%d")},'
                           f'結束日期 {end_time.strftime("%Y%m%d")}\n')
                for j in range(len(stock_ids)):
                    content += (f'股票代號：{stock_ids[j]}\t'
                                f'每月內部報酬率:{irrs[j]}\t'
                                f'總額投入報酬率:{bnhs[j]}\n')
                content += f'變異{i + 1}次，平均內部報酬率:{sum(irrs) / len(irrs)}，平均總額投入報酬率:{sum(bnhs) / len(bnhs)}\n)'
                content += f'原始數據{raw_data}'
                f.write(content)
            print("寫入" + write_folder + str(count))
            break

    # 判斷是否更改變異
    if sum(irrs) / len(irrs) > irr_:
        print("更改變異提示為:", p_mutate_2)
        p_mutate = p_mutate_2
        irr_ = sum(irrs) / len(irrs)

# todo testing
