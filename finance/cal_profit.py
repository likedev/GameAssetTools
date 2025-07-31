import adata
import pandas as pd
adata.proxy(is_proxy=True, ip='127.0.0.1:7890')


pd.set_option('display.max_columns', None)

# k_type: k线类型：1.日；2.周；3.月 默认：1 日k
res_df = adata.stock.market.get_market(stock_code='301361', k_type=1, start_date='2025-01-01')

print(res_df)
