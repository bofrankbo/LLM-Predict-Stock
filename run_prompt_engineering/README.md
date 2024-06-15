# Prompt Engineering 🛠️
使用大型語言模型來預測股票價格。

## 檔案說明 📁
檔案開頭
- `out`：程式碼的輸出結果。
- `run`：主要的執行檔，利用新聞內容或標題進行預測。
- `run_kline`：專門用於判斷 k 線的程式，不需要新聞內容。
- `eval`：用於計算預測效果的程式。

## 方法 🧪
- `prompt`：簡單判斷股票價格的漲跌。
- `mutate`：進行變異 prompt 的方法。
- `S2A`：System 2 Attention，一種注意力機制。
- `SBP`：Step Back Prompt，一種回溯的提示方法。

## 系統設定 ⚙️
- Python 版本：3.11.7

## 模型參數 🤖
我們使用的模型參數如下：
- 模型：gemini-1.5-flash / gemini-1.0-pro
- temperature：1
- topP：0.9