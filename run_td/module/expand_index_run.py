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
class ExpandIndexRun(FactorExpanding):
    def __init__(self, env, date, price_his):
        self.env = env
        self.date = date
        self.price_his = price_his
        self.path_expand = f"run_td/out_stock/Expands/UsableDT/{env['stock_id']}/expand.json" 
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
                    print(f"\t{stock} {str_news_date} news found")
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
        
        pre_date = self.date - timedelta(days=1)
        str_news_date = pre_date.strftime('%Y%m%d')
        str_sig_date = self.date.strftime('%Y%m%d')
        
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
        

        
        code_get_news, text_news = self.get_index_news(str_news_date, env["components"])
        
        if code_get_news == 1:
            print(f"Processing for date {str_sig_date}", end="")
            skeleton_res = {}
            batch = []
            question_key_list = []
            for key, factor in zip(key_list, value_list):
                # check if the factor is already processed
                if str_sig_date in output_data:
                    if key in output_data[str_sig_date]["skeleton"]:
                        skeleton_res[key] = output_data[str_sig_date]["skeleton"][key]
                        # print(f"\t{key} already processed, skip")
                        continue
                    
                # if is not processed, then generate the question
                if country == "us":
                    # print(f"\t{key} not processed yet")
                    messages = [
                        ("system", "You are an expert in the financial field and will answer users' questions about stock movment."),
                        ("human",
                        f"""
                        This is the possible stock price change factor {factor}
                        Please consider the following news. Will stocks rise or fall because of {factor}?
                        This is today's news: {text_news}
                        Please answer yes if it is likely to rise, answer no if it is likely to fall, and answer unknown if it is impossible to determine or irrelevant.

                        Respond in the following format. You only need to give a single judgment based on all the news headlines:
                        Judgment: #yes/#no/#unknown. Try to avoid answering "unknown."
                        Reason: Provide a **very brief** explanation in 1-2 sentences!
                        """)
                    ]
                    batch.append(messages)
                    question_key_list.append(key)
                elif country == "tw":
                    messages = [
                        ("system", "你是一個厲害的金融領域專家"),
                        ("human",
                        f"""
                        這是股價變動因素{factor}
                        請思考以下新聞，是否會因為{factor}而使股票上漲或下跌？
                        這是今天的新聞: {text_news}
                        如果可能上漲請回答yes，如果可能下跌則回答no，如果無法判斷或無關則回答unknown。

                        用以下格式回答，你只需要綜合所有的新聞給出一次的回答就好：
                        判斷結果: #yes/#no/#unknown 請盡量不要回答unknown
                        你的理由: **非常簡短**的用 1∼2 句話寫出來！
                        """)
                    ]
                    batch.append(messages)
                    question_key_list.append(key)
            
            if len(batch) > 0:
                res = self.llm.batch(batch)
            
                print("Ungenerated list", question_key_list)
                for idx, key in enumerate(question_key_list):
                    sig = 0
                    sig_str = res[idx].content.split("Reason")[0]
                    if "unknown" in sig_str:
                        sig = 0
                    elif "yes" in sig_str:
                        sig = 1
                    elif "no" in sig_str:
                        sig = -1

                    skeleton_res[key] = {
                        "response" : res[idx].content,
                        "sig" : sig,
                        "token": res[idx].usage_metadata
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