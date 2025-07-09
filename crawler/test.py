import pandas as pd
import os

# 讀取 CSV 檔案
str_d = '20250109'
path_raw = os.path.join(os.path.abspath(os.getcwd()), 'history_data','tw',f'fwbtin', f'fwbtin_{str_d}.csv')

df = pd.read_csv(path_raw, encoding='utf-8', header=[0, 1, 2])
print(df)

# 篩選臺股期貨的資料（商品名稱在第3列）
# df_tx = df[df[('Unnamed: 1_level_0', 'Unnamed: 1_level_1', '商品 名稱')] == '臺股期貨']
df_fwbtin = df[df[('Unnamed: 1_level_0', 'Unnamed: 1_level_1', '商品 名稱')] == '臺股期貨']

print(df_fwbtin)