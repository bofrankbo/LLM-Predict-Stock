from Track import Track

index_twii = [
    ["2308", "台達電", "tw"],
    ["2317", "鴻海", "tw"],
    ["2330", "台積電", "tw"],
    ["2382", "廣達", "tw"],
    ["2412", "中華電", "tw"],
    ["2454", "聯發科", "tw"],
    ["2881", "富邦金", "tw"],
    ["2882", "國泰金", "tw"],
    ["2891", "中信金", "tw"],
    ["6505", "台塑化", "tw"],
]

market_index = ["tx", "台灣指數期貨", "tw", index_twii]

env = {
    "stock_id": market_index[0],
    "stock_name": market_index[1],
    "country": market_index[2],
    "components" : market_index[3],
}

Track(env).run()