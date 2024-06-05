# LLM-Predict-Stock 📈

LLM-Predict-Stock 是一個強大的股票預測工具，它使用先進的機器學習技術來預測股票價格。

## 📁 檔案說明

### 🕷️ Crawler

我們的爬蟲程式分成四個報社。只需修改 "stock_id" 和 "網址"，就可以開始爬取資料。爬取的資料將儲存在 `stock_news` 資料夾中。

### 📈 price_history

我們提供了三種股價歷史資料：

- xxxx.csv：各個股票的股價，包含日期和開盤價。
- xxxxprice.csv：修正過的股價資料，用於 Gemini 評分。
- xxxxtwse.csv：從證交所抓取的資料，只包含上市公司的資料。

### 🚀 gemini 方法

Gemini 方法的執行步驟如下：

1. 依照評分買入股票
2. 計算 IRR(v2) 或 Return(v3)
3. 將 IRR(v2) 或 Return(v3) 比較高的指令重新變異
4. 最後測試

Gemini 方法的執行程式碼在 `run_gemini` 資料夾中。

### 📊 eval_data

我們提供了一些評估資料，包含了不同的評分方式和股票報酬率。

### 🤖 gemini api 模型參數

我們使用的 Gemini API 模型參數如下：

- 模型：gemini-1.0-pro
- 溫度：1
- topK：1.0
- topP：1.0

### 🧩 RAG 方法

RAG 方法的執行程式碼在 `run_rag` 資料夾中。我們使用了 Gemini、Ollama 和 TogetherAI 三種方法，並串接 Langchain 執行 RAG。

### 🎯 finetune 方法

Fine-tune 方法的執行程式碼在 `run_finetune` 資料夾中。

## 🎉 讓我們開始吧！

現在，您已經準備好使用 LLM-Predict-Stock 來預測股票價格了！如果您有任何問題，請隨時提出。
