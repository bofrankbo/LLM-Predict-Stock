import time
import os
import json
import pandas as pd
from datetime import datetime, timedelta

def factor_expanding(llm, env, key_list, value_list):
    st = datetime.strptime(env["start_date"], '%Y%m%d')
    et = datetime.strptime(env['end_date'], '%Y%m%d')
    stock_id = env['stock_id'] # 股票代號
    country = env['country'] # 國家

    # 讀取股價資料
    path_price_his = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/us/stock_price/{stock_id}.csv"
    df_price_his = pd.read_csv(path_price_his, encoding='utf-8')
    df_price_his['Date'] = pd.to_datetime(df_price_his['Date'], format='%Y%m%d')
    df_price_his = df_price_his[(st <= df_price_his['Date']) & (df_price_his['Date'] <= et)]

    # 讀取新聞資料
    path_news_file = os.path.dirname(os.path.abspath(os.getcwd())) + "/history_data/us/news_title/" + stock_id + "news_title.json"
    with open(path_news_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    # 讀取舊檔
    path_expand = f"{env['path_out']}{env['stock_id']}/expand.json"
    with open(path_expand, 'r') as f:
        old_data = json.load(f)

    # 輸出數據
    output_data = {}  
    for i in range(len(df_price_his)):
        # 取得前一日日期和新聞標題
        news_date = df_price_his.iloc[i]['Date'] - timedelta(days=1)
        str_news_date = news_date.strftime('%Y%m%d')
        if str_news_date in old_data["output_data"]:
            print(f"Already processed for date {str_news_date}, skip this date")
            continue
        print(f"Processing for date {str_news_date}")
        
        text_news = "today's news: \n"
        if str_news_date in news_data:
            news_list = news_data[str_news_date]
            for news in news_list:
                headline = news.get("headline")
                content = news.get("content")
                text_news += f"### {headline}\n{content}\n\n"
            # print(text_news)

            batch = []
            for factor in value_list:
                if country == "us":
                    messages = [
                        ("system", "You are an expert in the financial field and will answer users' questions about stock day trading."),
                        ("human",
                        f"""
                        This is the news: {text_news}
                        If it aligns with what {factor} represents as positive news, answer "yes." If it is negative news, answer "no." If it is indeterminate, answer "unknown."

                        Respond in the following format. You only need to give a single judgment based on all the news headlines:
                        Judgment: #yes/#no/#unknown. Try to avoid answering "unknown."
                        Reason: Provide a **very brief** explanation in 1-2 sentences!
                        """)
                    ]
                elif country == "tw":
                    messages = [
                        ("system", "你是一個厲害的金融領域專家"),
                        ("human",
                        f"""
                        這是新聞標題{text_news}
                        如果有符合{factor}所表示的利多請回答yes，如果是利空則回答no，如果無法判斷則回答unknown。

                        用以下格式回答，你只需要綜合所有的新聞給出一次的回答就好：
                        判斷結果: #yes/#no/#unknown 請盡量不要回答unknown
                        你的理由: **非常簡短**的用 1∼2 句話寫出來！
                        """)
                    ]
                batch.append(messages)
            # res = llm.batch(batch)
            res = ""
            date_str = df_price_his.iloc[i]['Date'].strftime('%Y%m%d')
            skeleton_res = {}
            for i in range(len(res)):
                sig = 0
                sig_str = res[i].content.split("Reason")[0]
                if "unknown" in sig_str:
                    sig = 0
                elif "yes" in sig_str:
                    sig = 1
                elif "no" in sig_str:
                    sig = -1

                skeleton_res[key_list[i]] = {
                    "response" : res[i].content,
                    "sig" : sig,
                    "token": res[i].usage_metadata
                }
            
            output_data[date_str] = {
                "skeleton": skeleton_res,
            }

        else:
            print(f"\tNo news found for date {str_news_date}, skip this date")

    # 將所有輸出數據寫入到同一個dictioanry中
    data = {
        "model": llm.model_name,
        "temperature": llm.temperature,
        "stock_id": stock_id,
        "output_data": output_data,
    }
    
    return data