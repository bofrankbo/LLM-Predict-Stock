import os
import json
import re
import textwrap
import pandas as pd
from datetime import datetime, timedelta
from module.expand_stock import Expanding 


# 儲存的日期是判斷日期，非新聞日期
# 以判斷日期為準
class Index_UsableExpanding(Expanding):
    def __init__(self, env, llm, price_his):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_expand = f"out_stock/Expands/FactorUsable/{env['stock_id']}/expand.json"    # 輸出 JSON 檔案
        
    def expanding(self, factors):
        '''
            llm_factors: list of factors
            
            update factors.json
            it can generate new factors while old factors are not empty
            if old data is empty, then create a new one
        '''
        env = self.env
        stock_id = env['stock_id'] # 股票代號
        country = env['country'] # 國家
        st = datetime.strptime(env['start_date'], '%Y%m%d')
        et = datetime.strptime(env['end_date'], '%Y%m%d')
        df_price_his = self.price_his.copy()
        df_price_his['Date'] = pd.to_datetime(df_price_his['Date'], format='%Y%m%d')
        df_price_his = df_price_his[(st <= df_price_his['Date']) & (df_price_his['Date'] <= et)]
        
        key_list = list(factors.keys())
        value_list = list(factors.values())

        old_data = None
        if os.path.exists(self.path_expand):
            with open(self.path_expand, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        
        # make old_data if old_data exists
        if old_data is None:
            output_data = {}
        else:
            output_data = old_data['output_data']
            
        # iterate through each date, and generate new data
        for i in range(len(df_price_his)):
            
            # get T-1 date
            news_date = df_price_his.iloc[i]['Date'] - timedelta(days=1)
            str_news_date = news_date.strftime('%Y%m%d')

            # get T date
            str_sig_date = df_price_his.iloc[i]['Date'].strftime('%Y%m%d')
            
            if str_sig_date in output_data:
                # print(f"\t{str_sig_date} already processed, skip")
                continue
            print(f"Processing for date {str_sig_date}", end="")

            text_news = "today's news: \n"
            hasnews = False
            for stock in env["components"]:
                
                path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{stock[2]}/news_title/{stock[0]}news_title.json"
                with open(path_news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
            
                if str_news_date not in news_data:
                    print(f"\t{stock[0]} date {str_news_date} was not fetched, skip {str_sig_date}")
                    continue    

                news_list = news_data[str_news_date]

                if len(news_list) > 0:
                    # print(f"\t{stock[0]} {str_news_date} news found")
                    hasnews = True
                    for news in news_list:
                        headline = news.get("headline")
                        # content = news.get("content")
                        # text_news += f"### {headline}\n{content}\n\n"
                        text_news += f"{headline}\n"
                else:
                    # print(f"\t{stock[0]} no news found in {str_news_date}")
                    pass
                    # print(text_news)
                
            if hasnews:
                print(f"\t{str_news_date} news found")
                batch = []
                for factor in value_list:
                    if country == "us":
                        messages = [
                            ("system", "You are an expert in the financial field and will answer users' questions about stock movment."),
                            ("human",
                            textwrap.dedent(f"""
                            If bad news affects the stock price but does not significantly impact the company’s future outlook, it is often a good investment opportunity.

                            Please evaluate the following news:
                            Will it severely impact the future economy due to {factor}?

                            Today’s news: {text_news}

                            If the future economic outlook is not seriously challenged, reply yes.
                            If the economy will face severe negative impacts in the future, reply no.
                            If it is uncertain, reply unknown.
                            
                            Respond in the following format. You only need to give a single judgment based on all the news headlines:
                            Judgment: #yes/#no/#unknown. Try to avoid answering "unknown."
                            Reason: Provide a **very brief** explanation in 1-2 sentences!
                            """).strip())
                        ]
                        # messages = [
                        #     ("system", "You are an expert in the financial sector."),
                        #     ("human",
                        #     textwrap.dedent(f"""
                        #     Here is a stock price influencing factor: {factor}
                        #     Please analyze the following news and determine whether it is likely to cause the stock price to rise or fall due to {factor}.

                        #     Today's news: {text_news}
                        #     If the stock is likely to rise, answer **yes**.  
                        #     If the stock is likely to fall, answer **no**.  
                        #     If it is uncertain or unrelated, answer **unknown**.

                        #     Respond in the following format, providing only **one** overall judgment:  
                        #     **Result:** #yes / #no / #unknown (Try to avoid answering "unknown.")  
                        #     **Reason:** Provide a **very brief** explanation in **1-2 sentences**!
                        #     """).strip())
                        # ]
                    elif country == "tw":
                        messages = [
                            ("system", "你是一個厲害的金融領域專家"),
                            ("human",
                            textwrap.dedent(f"""
                            這是股價變動因素{factor}
                            請思考以下新聞，是否會因為{factor}而使股票上漲或下跌？
                            這是今天的新聞: {text_news}
                            如果可能上漲請回答yes，如果可能下跌則回答no，如果無法判斷或無關則回答unknown。

                            用以下格式回答，你只需要綜合所有的新聞給出一次的回答就好：
                            判斷結果: #yes/#no/#unknown 請盡量不要回答unknown
                            你的理由: **非常簡短**的用 1∼2 句話寫出來！
                            """).strip())
                        ]
                    batch.append(messages)
                res = self.llm.batch(batch)
                # res = ""
                
                skeleton_res = {}
                for i in range(len(res)):
                    sig = 0
                    # Reason or 你的理由 
                    sig_str = re.split(r"Reason|你的理由", res[i].content)[0]
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
            else:
                print(f"\t no news found in {str_news_date}")
                skeleton_res = {}
                for i in range(len(value_list)):
                    skeleton_res[key_list[i]] = {
                        "response" : "No news found",
                        "sig" : 0,
                        "token": ""
                    }
        
            output_data[str_sig_date] = {
                "skeleton": skeleton_res,
            }
        
            # print(output_data.keys())
        # 排序output_data的資料
        output_data = dict(sorted(output_data.items(), key=lambda x: x[0]))

        # 將所有輸出數據寫入到同一個dictioanry中
        data = {
            "model": self.llm.model_name,
            "temperature": self.llm.temperature,
            "stock_id": stock_id,
            "output_data": output_data,
        }
        
        os.makedirs(os.path.dirname(self.path_expand), exist_ok=True)
        with open(self.path_expand, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data