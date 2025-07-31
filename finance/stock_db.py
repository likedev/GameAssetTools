import akshare as ak
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import time
import adata
import pandas as pd
import numpy as np

adata.proxy(is_proxy=True, ip='127.0.0.1:7890')

# --- 数据库配置 ---
# 请根据您的MySQL服务器信息修改以下配置
DB_CONFIG = {
    'user': 'root',  # 数据库用户名
    'password': 'root',  # 数据库密码
    'host': 'localhost',  # 数据库主机，本地一般是 localhost 或 127.0.0.1
    'port': 3306,  # 数据库端口，MySQL 默认是 3306
    'database': 'stock'  # 您创建的数据库名称
}

# --- 全局变量 ---
# 创建数据库引擎

mysql_engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


def load_all_stock():
    query = text(f"SELECT * FROM stock ")
    with mysql_engine.connect() as connection:
        df = pd.read_sql(query, connection)
        df_indexed = df.set_index('代码')
        return df_indexed


def select_wencai(sql):
    query = text(sql)
    with mysql_engine.connect() as connection:
        df = pd.read_sql(query, connection)
        df_indexed = df.set_index('代码')
        return df_indexed


def update_stock(time,code):
    pass
