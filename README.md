# LLM-Predict-Stock 📈

LLM-Predict-Stock 是一個強大的股票預測工具，它使用先進的機器學習技術來預測股票價格。

## 目錄

- [Crawler](/crawler/)
- [History Data](/history_data/)
- [Backtest LLM factor](/backtest_llm_factor/)
- [RAG 方法](/run_rag/)
- [Fine-tune 方法](/run_finetune/)

## History Data
### Crawler 🕷️
1. 新聞 /news  
我們的爬蟲程式分成四個報社。只需修改 "stock_id" 和 "網址"，就可以開始爬取資料。爬取的資料將儲存在 `stock_news` 資料夾中。
2. 新聞標題 /new_title.py  
從google爬下來的新聞標題資料

3. 台股資料 /price_stock_tw.ipynb  
從台灣期貨交易所爬下來的資料
4. 台股資料 /price_stock_us.ipynb  
前往nasdaq網站下載資料在執行轉換成我們的格式

### Data 📈
- `stock_news`：爬取四家報社的歷史新聞資料，包含自由、鉅亨、tvbs、中時。
- `price history`：個股股價資料：
  - xxxx.csv（舊版）：各個股票的股價，包含日期和開盤價。
  - xxxxprice.csv（舊版）：修正過的股價資料
  - xxxxtwse.csv：從證交所抓取的資料，只包含上市公司的資料。


- 其他資料[這裡](https://drive.google.com/drive/folders/1L-pGrVa4V3i1z3XF1vpQe-qZtFHOS6cG?usp=sharing)下載資料。

  - 期貨：期交所成立～2020的逐比成交資料，2023 5月～現在的逐比成交資料
  - 三大法人買賣超：期交所成立～現在的三大法人買賣超

## Factor
主要包含 Prompt Engineering 以及 RAG 結合 GA 的作法

## Backtest LLM factor 📊

主要包含 Prompt Engineering 結合 GA 的作法

## RAG 方法 🧩

RAG 方法的執行程式碼在 `run_rag` 資料夾中。串接 Langchain 執行 RAG。

## Fine-tune 方法 🎯

Fine-tune 方法的執行程式碼在 `run_finetune` 資料夾中。