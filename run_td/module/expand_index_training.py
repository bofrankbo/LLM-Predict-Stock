import os
import json
import re
import textwrap
import pandas as pd
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI

from module.expand_stock import FactorExpanding

# 儲存的日期是判斷日期，非新聞日期
# 以判斷日期為準
class ExpandIndex(FactorExpanding):
    def __init__(self, env, llm, price_his):
        self.env = env
        self.llm = llm
        self.price_his = price_his
        self.path_expand = f"run_td/out_stock/Expands/FactorUsable/{env['stock_id']}/expand.json" 
        self.llm = ChatOpenAI(
            openai_api_key = os.getenv('OPENAI_API_KEY'),
            model='gpt-4o-mini',
            temperature=1,
        )
        
        # history data path
        self.path_news_file = f"{os.path.dirname(os.path.abspath(os.getcwd()))}/history_data/{env['country']}/news_title/{env['stock_id']}news_title.json"
    
    def get_index_news(self, str_news_date, components):
        # return int, 1 means has news, 0 means no news, -1 means news did not fetch
        hasNews = False
        text_news = "today's news: \n"
        for stock in components:
            path_news_file = f"{os.getcwd()}/history_data/{stock[2]}/news_titles/{stock[0]}news_title.json"
            with open(path_news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            try:
                news_list = news_data[str_news_date]
                hasNews = True
                if len(news_list) > 0:
                    print(f"\t{stock[0]} date {str_news_date} news found")
                    for news in news_list:
                        headline = news.get("headline")
                        # content = news.get("content")
                        # text_news += f"### {headline}\n{content}\n\n"
                        text_news += f"{headline}\n"
            except Exception as e:
                print(f"\t{stock[0]} date {str_news_date} was not fetched, skip")
                return -1, ''
        
        if hasNews == False:
            return 0, 'No news found'
        else:
            return 1, text_news
            
        
    def expanding(self, factors):
        '''
            llm_factors: list of factors
            
            update factors.json
            it can generate new factors while old factors are not empty
            if old data is empty, then create a new one
        '''
        env = self.env
        stock_id = env['stock_id']
        country = env['country']
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
            
        
        
        news_date = df_price_his.iloc[i]['Date'] - timedelta(days=1)    # get T-1 date
        str_news_date = news_date.strftime('%Y%m%d')
        str_sig_date = df_price_his.iloc[i]['Date'].strftime('%Y%m%d')  # get T date

        print(f"Processing for date {str_sig_date}", end="")
        code_get_news, text_news = self.get_index_news(str_news_date, env["components"])
        
        if code_get_news == 1:
            skeleton_res = {}
            batch = []
            question_key_list = []
            for key, factor in zip(key_list, value_list):
                if str_sig_date in output_data:
                    if key in output_data[str_sig_date]["skeleton"]:
                        skeleton_res[key] = output_data[str_sig_date]["skeleton"][key]
                        # print(f"\t{key} already processed, skip")
                
                elif country == "us":
                    # print(f"\t{key} not processed yet")
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
                    batch.append(messages)
                    question_key_list.append(key)
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
                    question_key_list.append(key)
            res = self.llm.batch(batch)
            
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
            # print("skeleton_res", skeleton_res.keys())
        elif code_get_news == 0:
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
        # print("output_data", output_data[str_sig_date])
            
        # sort output_data by date
        # save output_data to json file
        output_data = dict(sorted(output_data.items(), key=lambda x: x[0]))
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