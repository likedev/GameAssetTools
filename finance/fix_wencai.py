import pandas as pd
import akshare as ak
from tqdm import tqdm
import time
import stock_db

import pymysql

DB_CONFIG = {
    'user': 'root',  # 数据库用户名
    'password': 'root',  # 数据库密码
    'host': 'localhost',  # 数据库主机，本地一般是 localhost 或 127.0.0.1
    'port': 3306,  # 数据库端口，MySQL 默认是 3306
    'database': 'stock'  # 您创建的数据库名称
}


def get_his_price(code, target_date):
    price_dict = {}
    time.sleep(1)
    date_formated = target_date.replace('-', '')
    try:
        # 获取指定日期的历史数据，使用前复权 'qfq'
        stock_df = ak.stock_zh_a_hist(symbol=code,
                                      period="daily",
                                      start_date=date_formated,
                                      end_date=date_formated,
                                      adjust="qfq")

        # 如果当天有数据（未停牌）
        if not stock_df.empty:
            # 提取当天的收盘价
            price = stock_df['收盘'].iloc[0]
            price_dict[code] = price
            return price
    except Exception as e:
        # print(f"\n获取股票 {code} 数据时出错: {e}")
        pass  # 出错时直接跳过


df = stock_db.select_wencai("select * from wencai where 时间 = '2025-07-30晚选' ")

db_conn = pymysql.connect(**DB_CONFIG)
for index, row in df.iterrows():
    # print(index,row)
    # exit()
    price = get_his_price(index, "2025-07-30")

    sql = " update wencai set  最新价 = '%s' where 代码 = '%s' and 时间 = '2025-07-30晚选' " % (str(price) + '', index)
    print(sql)

    cursor = db_conn.cursor()
    cursor.execute(sql)

db_conn.commit()
