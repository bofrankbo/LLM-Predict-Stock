# 檔案說明
## Crawler 
爬蟲程式 分成4個報社  
修改裡面的 "stock_id" 以及 "網址" 就可以爬了  
資料會存在 stock_news 中  
## price_history
(舊版)xxxx.csv 各個股票的股價 [日期,開盤]  
xxxxprice.csv 新版資訊比較完整 dataframe

# gemini 作法
資料夾在 run_gemini

1.依照評分買入股票  
2.最後計算IRR or Retrun  
3.將 IRR or Retrun 比較高的指令重新變異  
4.最後測試
![image](https://github.com/Atomuze/LLM-Predict-Stock/assets/46251744/a9e9e674-9309-4d9a-84a6-16a908aecc04)
![image](https://github.com/Atomuze/LLM-Predict-Stock/assets/46251744/470109c7-3961-4fa2-9288-82d535db331e)

## eval_data
20 ~ 51 -100~100  
88 ~ 137 -100~100  
157 ~ 235 #非常好(2) #好(1) #無關(0) #不好(-1) #非常不好(-2)  

20230101 ~ 20231231 一年的前5擋股票報酬率 1.405046  
20230101 ~ 20231231 一年的後5擋股票報酬率 1.5045   
20220101 ~ 20231231 兩年的10擋股票報酬率 1.186132  
20230101 ~ 20231231 一年的10擋股票報酬率 1.170022  


## gemini api 模型參數

models/gemini-1.0-pro  
temperature 1  
topK 1.0  
topP 1.0

# RAG 作法
資料夾在 run_rag

# finetune 作法
資料夾在 run_finetune
