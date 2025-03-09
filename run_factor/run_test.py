from TV_usableexp_dt_thres_stock import TV_UsableExpThresDT
import os
import pandas as pd
import multiprocessing as mp
from datetime import datetime

# CSV 檔案存儲，避免記憶體過載
RESULTS_FILE = "avgs_results.csv"

import pandas as pd
from datetime import datetime

# 買進賣出需要的手續費
fee = {
    "tax_stock": 0.003,  # 賣出0.003
    "tax_future": 0.00002 * 2,  # 買進與賣出各0.00002
    "fee_stock": 0.001425 * 2,  # 券商手續費公道價，買進與賣出各0.001425
    "fee_future": 0.00002 * 2,  # 各家不大相同，以交易稅計算
    "sliding_price": 0.00001,  # 滑價
}

# 股票清單
# tw_index_fee = 0
tw_stock_fee = 0
# tw_stock_fee = fee["tax_stock"] + fee["fee_stock"] + fee["sliding_price"]
tw_index_fee = fee["tax_future"] + fee["fee_future"] + fee["sliding_price"]

data = [
    ["2330", "台積電", "tw"],
    ["2308", "台達電", "tw", tw_stock_fee],
    ["2317", "鴻海", "tw", tw_stock_fee],
    ["2382", "廣達", "tw", tw_stock_fee],
    ["2412", "中華電", "tw", tw_stock_fee],
    ["2454", "聯發科", "tw", tw_stock_fee],
    ["2881", "富邦金", "tw", tw_stock_fee],
    ["2882", "國泰金", "tw", tw_stock_fee],
    ["2891", "中信金", "tw", tw_stock_fee],
    ["6505", "台塑化", "tw", tw_stock_fee],
    ["3231", "緯創", "tw"],
    ["2207", "和泰車", "tw"],
    ["3661", "世芯", "tw"],
    ["2603", "長榮", "tw"],
    ["2408", "南亞科", "tw"],
    
    # ["6214", "精誠", "tw"],
    # ["3045", "台灣大", "tw"],
    # ["2379", "瑞昱", "tw"],
    # ["2357", "華碩", "tw"],
    # ["2345", "智邦", "tw"],
]

data_range_tv = [
    # ["20220101", "20220110", 15.5], # test
    ["20220101", "20241231", 1], # tv1
    ["20220101", "20241231", 2], # tv2
    ["20220101", "20241231", 3], # tv3
    ["20220101", "20241231", 4], # tv4
    ["20220101", "20241231", 5], # tv5
    ["20220101", "20241231", 6], # tv6
    ["20220101", "20241231", 7], # tv7
    ["20220101", "20241231", 8], # tv8
    ["20220101", "20241231", 9], # tv9
    ["20220101", "20241231", 10], # tv10
    ["20220101", "20241231", 11], # tv11
    ["20220101", "20241231", 12], # tv12
    ["20220101", "20241231", 13], # tv13
    ["20220101", "20241231", 14], # tv14
    ["20220101", "20241231", 15], # tv15
    ["20220101", "20241231", 16], # tv16
    ["20220101", "20241231", 17], # tv17
    ["20220101", "20241231", 18], # tv18
    ["20220101", "20241231", 19], # tv19
    ["20220101", "20241231", 20], # tv20    
    ["20220101", "20241231", 21], # tv21
    ["20220101", "20241231", 22], # tv22
    ["20220101", "20241231", 23], # tv23
    ["20220101", "20241231", 24], # tv24
    ["20220101", "20241231", 25], # tv25
    ["20220101", "20241231", 26], # tv26
    ["20220101", "20241231", 27], # tv27
    ["20220101", "20241231", 28], # tv28
    ["20220101", "20241231", 29], # tv29
    ["20220101", "20241231", 30], # tv30
]

def get_balance_list(list_rtn, start_price):
    balance = start_price
    list_balance = [start_price]
    for rtn in list_rtn[1:]:
        balance = balance * (1 + float(rtn))
        list_balance.append(balance)
    return list_balance

def cacl_avg(df_stocks_results, wincount=None, ttl_count=None):
    '''
        only return average row
    '''
    
    average_row = pd.DataFrame()
    average_row['tp'] = [df_stocks_results['tp'].sum()]
    average_row['fp'] = [df_stocks_results['fp'].sum()]
    average_row['tn'] = [df_stocks_results['tn'].sum()]
    average_row['fn'] = [df_stocks_results['fn'].sum()]
    average_row['accuracy'] = (average_row['tp'] + average_row['tn']) / (average_row['tp'] + average_row['tn'] + average_row['fp'] + average_row['fn'])
    average_row['precision'] = average_row['tp'] / (average_row['tp'] + average_row['fp'])
    # EV 算法 每個ev成上avail_count 總和後再除上 avail_count 的平均
    average_row['avail_count'] = [df_stocks_results['avail_count'].sum()]
    average_row['pci_avl_count'] = [df_stocks_results['tp'].sum() + df_stocks_results['fp'].sum()]
    average_row['ev'] = (df_stocks_results['ev'].astype(float) * df_stocks_results['avail_count']).sum() / df_stocks_results['avail_count'].sum()
    average_row['precision_ev'] = (df_stocks_results['precision_ev'].astype(float) * (df_stocks_results['tp'] + df_stocks_results['fp'])).sum() / (df_stocks_results['tp'].sum() + df_stocks_results['fp'].sum())
    if ttl_count is None:
        average_row['win B&H'] = None
    else:
        average_row['win B&H'] = round(wincount / ttl_count, 2)
        
    if 'B&H' in df_stocks_results.columns:
        average_row['B&H'] = df_stocks_results['B&H'].mean()
    if 'RTN' in df_stocks_results.columns:
        average_row['RTN'] = df_stocks_results['RTN'].mean()
    
    return average_row

def run_stock(stock, i):
    selected_columns = ['accuracy', 'precision', 'ev', 'precision_ev', 'avail_count', 'tp', 'fp', 'tn', 'fn']
    stock_results = []
    stock_avg_list = []  

    for date_range in data_range_tv:
        env = {
            "stock_id": stock[0],
            "stock_name": stock[1],
            "country": stock[2],
            "start_date": date_range[0],
            "end_date": date_range[1],
            "tv": date_range[2],
            "run_count": str(i)
        }
        print(env['stock_id'], env['stock_name'], env['country'], f"tv{date_range[2]}")

        eval_module = TV_UsableExpThresDT(env)
        eval_module.run()
        train_datarange, test_datarange = eval_module.split_exp(date_range[2])
        
        mode = 1
        eval_module.training(mode, train_datarange, test_datarange)

        result = eval_module.get_result(1)  
        result_train = result["train"]
        result_test = result["test"]

        list_stock = [result_test]

        # Training & Test 計算
        train_date, train_bnh_balance, train_stag_rtn = eval_module.get_return_list('train')
        train_stag_balance = get_balance_list(train_stag_rtn, train_bnh_balance[0])
        list_date, list_bnh_balance, list_stag_rtn = eval_module.get_return_list('test')
        list_stag_balance = get_balance_list(list_stag_rtn, list_bnh_balance[0])

        train_N_days = (datetime.strptime(sorted(train_datarange.keys())[-1], '%Y%m%d') - 
                        datetime.strptime(sorted(train_datarange.keys())[0], '%Y%m%d')).days

        test_N_days = (datetime.strptime(sorted(test_datarange.keys())[-1], '%Y%m%d') - 
                       datetime.strptime(sorted(test_datarange.keys())[0], '%Y%m%d')).days

        stock_avg = cacl_avg(pd.DataFrame(list_stock).loc[:, selected_columns])
        stock_avg['stock_id'] = stock[0]
        stock_avg['tv'] = date_range[2]

        # Training & Test 年化報酬率
        stock_avg['Train_RTN'] = (train_stag_balance[-1] / train_bnh_balance[0] - 1) * 100
        stock_avg['Train_B&H'] = (train_bnh_balance[-1] / train_bnh_balance[0] - 1) * 100
        stock_avg['Ann_Train_RTN'] = ((1 + stock_avg['Train_RTN'] / 100) ** (252 / train_N_days) - 1) * 100
        stock_avg['Ann_Train_B&H'] = ((1 + stock_avg['Train_B&H'] / 100) ** (252 / train_N_days) - 1) * 100
        stock_avg['RTN'] = (list_stag_balance[-1] / list_bnh_balance[0] - 1) * 100
        stock_avg['B&H'] = (list_bnh_balance[-1] / list_bnh_balance[0] - 1) * 100
        stock_avg['Ann_RTN'] = ((1 + stock_avg['RTN'] / 100) ** (252 / test_N_days) - 1) * 100
        stock_avg['Ann_B&H'] = ((1 + stock_avg['B&H'] / 100) ** (252 / test_N_days) - 1) * 100
        stock_avg['win B&H'] = "yes" if list_stag_balance[-1] > list_bnh_balance[-1] else "no"

        stock_avg_list.append(stock_avg)

    if stock_avg_list:
        stock_avg_df = pd.concat(stock_avg_list)
        # 直接寫入 CSV，減少記憶體占用
        stock_avg_df.to_csv(RESULTS_FILE, mode='a', index=False, header=not os.path.exists(RESULTS_FILE))
        return stock_avg_df
    return None

def runAll_parallel(i):
    num_workers = min(mp.cpu_count(), len(data))  # 限制 CPU 使用數
    print(f"Using {num_workers} CPU cores.")

    with mp.Pool(processes=num_workers) as pool:
        results = pool.starmap(run_stock, [(stock, i) for stock in data])

    results = [r for r in results if r is not None]
    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

if __name__ == "__main__":  # 這行是 Mac 上 **multiprocessing 必須的**
    for i in range(1):
        print(i+1)
        avgs = runAll_parallel(i+1)

    # 計算 TV 總平均
    tv_avg_df = avgs.groupby("tv").mean().reset_index()
    print(tv_avg_df.loc[:, ["tv", "Ann_Train_RTN", "Ann_Train_B&H", "Ann_RTN",  "Ann_B&H", "Win B&H", "Diff"]])