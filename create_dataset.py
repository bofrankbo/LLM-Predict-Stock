import pandas as pd
import datasets
from datasets import Dataset, DatasetDict

id = ["20230906","20231122"]

text = ["今年5月中捷列車撞上興富發建案掉落的吊臂釀1死14傷，全台中運量無人駕駛車站增設月台緊急停車鈕，中捷市政府站6日正式啟用。中捷公司表示，全線18個車站將於今年底前完成設置。","第12款符合條款第四條第XX款：12事實發生日：112/11/231.召開法人說明會之日期：112/11/232.召開法人說明會之時間：14 時 00 分3.召開法人說明會之地點：統一證券集團大樓15F會議室(台北市松山區東興路8號15F)4.法人說明會擇要訊息：本公司受邀參加統一綜合證券舉辦之法人說明會，會中說明本公司之財務及營運概況。5.其他應敘明事項：無完整財務業務資訊請至公開資訊觀測站之法人說明會一覽表或法說會項目下查閱。"]
response = ["10","50"]

tdf = pd.DataFrame({"id": id, "text": text, "response": response})
vdf = pd.DataFrame({"id": id, "text": text, "response": response})
ted = pd.DataFrame({"id": id, "text": text, "response": response})

tds = Dataset.from_pandas(tdf)
vds = Dataset.from_pandas(vdf)
ted = Dataset.from_pandas(ted)

ds = DatasetDict()

ds['train'] = tds
ds['validation'] = vds
ds['test'] = ted

print(ds)
ds.push_to_hub(repo_id="Atomuze/stock_news_score", private=True)