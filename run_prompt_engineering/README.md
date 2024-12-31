# Prompt Engineering 🛠️
使用大型語言模型來預測股票漲跌

## 檔案說明 📁
### 檔案開頭
- `out`：程式碼的輸出檔案
- `run`：主要的執行檔，利用新聞內容或標題進行預測。
- `eval`：用於計算預測效果的程式。  
### 檔案後綴
- `kline`：專門用於判斷 k 線的程式，不需要新聞內容
- `twii`：專門用於新聞和台指期關係的程式
- `stock`：專門用於新聞和股票關係的程式


## 方法 🧪
- `prompt`：簡單判斷股票價格的漲跌。
- `mutate`：進行變異 prompt 的方法。
- `S2A`：System 2 Attention，一種注意力機制。
- `SBP`：Step Back Prompt，一種回溯的提示方法。
- `GA`：選擇幾種 Factor 做為判斷依據，再演化這些 Factor 選出最佳解，Factor 演化後再判斷
    - `GA_factor`：Factor 都先判斷完後再演化


## 系統設定 ⚙️
- Python 版本：3.11.7

## 模型參數 🤖
我們使用的模型參數如下：
- 模型：gpt4o-mini / gemini-1.5-flash / gemini-1.0-pro
- temperature：各模型預設值
- topP：各模型預設值