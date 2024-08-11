import baostock as bs
import pandas as pd

# 登录系统
lg = bs.login()

# 获取股票的历史数据
stock_code = "sz.002400"  # 例如，使用上海银行的股票代码
query_history_k = bs.query_history_k_data_plus(stock_code,
                                               "date,open,high,low,close,volume",
                                               start_date='2024-01-01', end_date='2024-08-11',
                                               frequency="d", adjustflag="3")

# 读取数据
data_list = []
while (query_history_k.error_code == '0') & query_history_k.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(query_history_k.get_row_data())
result = pd.DataFrame(data_list, columns=query_history_k.fields)

# 登出系统
bs.logout()

print(result)
