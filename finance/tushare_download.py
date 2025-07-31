# -*- coding: utf-8 -*-

import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import time

# --- 1. 配置信息 (请务必修改为你自己的信息) ---

# Tushare Pro API Token
TUSHARE_TOKEN = "1efbcc304d1d92587a966689ed3aac0a5234069a4550c7cc402dd8b0"

# MySQL 数据库连接信息
DB_USER = "root"  # 数据库用户名
DB_PASS = "root"  # 数据库密码
DB_HOST = "127.0.0.1"  # 数据库主机地址
DB_PORT = 3306  # 数据库端口
DB_NAME = "stock"  # 数据库名称

# --- 2. 初始化 ---

# 初始化 Tushare Pro API
try:
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    print("Tushare API 初始化成功。")
except Exception as e:
    print(f"Tushare API 初始化失败: {e}")
    exit()

# 初始化数据库连接引擎 (Engine)
# 使用 f-string 构造连接字符串，确保兼容性和安全性
try:
    db_conn_str = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_conn_str)
    print("数据库连接引擎创建成功。")
except Exception as e:
    print(f"数据库连接引擎创建失败: {e}")
    exit()


def update_stock_basic_info():
    """
    获取所有A股的基本信息和最新的每日指标，并存入 stock_basic_info 表。
    该函数会先清空表，然后插入最新数据，确保数据是当前最新的快照。
    """
    print("\n===== 开始更新股票基本信息与每日指标 =====")
    try:
        # 获取股票列表基本信息
        print("正在获取所有A股列表...")
        stock_list = pro.stock_basic(exchange='', list_status='L',
                                     fields='ts_code,symbol,name,area,industry,market,list_date')
        if stock_list.empty:
            print("未能获取到股票列表，请检查Tushare Token或网络。")
            return None
        print(f"成功获取 {len(stock_list)} 只股票的基本信息。")

        # 获取所有股票最新交易日的每日指标
        print("正在获取所有A股最新的每日指标（市盈率、市值等）...")
        daily_basic_data = pro.daily_basic(
            ts_code='',
            trade_date='',
            fields='ts_code,trade_date,close,pe,pb,total_mv,circ_mv'
        )
        if daily_basic_data.empty:
            print("未能获取到每日指标数据，可能是非交易日或API问题。")
            return None
        print(f"成功获取 {len(daily_basic_data)} 条最新的每日指标数据。")

        # 合并数据
        print("正在合并基本信息和每日指标...")
        df = pd.merge(stock_list, daily_basic_data, on='ts_code', how='left')

        # 筛选掉没有最新交易数据的股票（比如当天停牌的）
        df.dropna(subset=['trade_date'], inplace=True)

        # 将总市值和流通市值从万元转换为亿元
        df['total_mv'] = df['total_mv'] / 10000
        df['circ_mv'] = df['circ_mv'] / 10000

        print(f"数据合并完成，准备写入数据库的记录共 {len(df)} 条。")

        # 使用 to_sql 写入数据库
        # 我们采用先清空表再追加的方式，保证数据是最新快照
        with engine.connect() as conn:
            # 开启事务
            trans = conn.begin()
            try:
                print("正在清空 stock_basic_info 表...")
                conn.execute('TRUNCATE TABLE stock_basic_info;')
                print("正在将最新数据写入 stock_basic_info 表...")
                df.to_sql('stock_basic_info', con=conn, if_exists='append', index=False)
                trans.commit()  # 提交事务
                print("股票基本信息与每日指标更新成功！")
            except Exception as e:
                trans.rollback()  # 如果发生错误，回滚事务
                print(f"写入 stock_basic_info 表失败: {e}")
                return None

        return df['ts_code'].tolist()

    except Exception as e:
        print(f"更新股票基本信息过程中发生错误: {e}")
        return None


def update_stock_daily_price(stock_codes):
    """
    获取并存储指定股票列表的近3年历史日线行情（前复权）。
    使用 'append' 模式写入，利用数据库的主键约束来避免重复数据。
    """
    if not stock_codes:
        print("没有需要更新历史行情的股票代码，任务结束。")
        return

    print("\n===== 开始更新近3年历史日线行情（前复权） =====")

    # 计算起始日期（3年前的今天）
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=3 * 365)).strftime('%Y%m%d')

    print(f"将获取从 {start_date} 到 {end_date} 的历史数据。")

    total = len(stock_codes)
    success_count = 0

    for i, code in enumerate(stock_codes):
        print(f"正在处理: {code} ({i + 1}/{total})...")
        time.sleep(0.5)
        try:
            # 使用 pro_bar 获取前复权日线行情
            df_daily = ts.pro_bar(
                ts_code=code,
                adj='qfq',
                start_date=start_date,
                end_date=end_date,
                # 选择我们需要的字段
                fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
            )

            if df_daily is None or df_daily.empty:
                print(f"未能获取到 {code} 的历史数据，跳过。")
                continue

            # 转换 trade_date 格式为 YYYY-MM-DD，以便写入 date 类型的数据库字段
            df_daily['trade_date'] = pd.to_datetime(df_daily['trade_date']).dt.date

            # 写入数据库，如果数据已存在，主键冲突会阻止插入重复数据
            df_daily.to_sql('stock_daily_price', con=engine, if_exists='append', index=False)

            success_count += 1
            print(f"  -> {code} 的 {len(df_daily)} 条历史数据写入成功。")
        except Exception as e:
            # 捕获可能的数据库主键冲突错误或其他异常
            if "Duplicate entry" in str(e):
                print(f"  -> {code} 的部分数据已存在，跳过重复部分。")
            else:
                print(f"  -> 处理 {code} 时发生错误: {e}")

    print(f"\n历史日线行情更新完成！共成功处理 {success_count}/{total} 只股票。")

if __name__ == '__main__':
    start_time = time.time()
    print("====== 股票数据同步任务开始 ======")

    # 第一步：更新股票基本信息表，并获取股票代码列表
    all_stock_codes = update_stock_basic_info()

    # 第二步：根据获取的股票代码列表，更新历史行情数据
    if all_stock_codes:
        update_stock_daily_price(all_stock_codes)

    end_time = time.time()
    print("\n====== 所有任务执行完毕 ======")
    print(f"总耗时: {((end_time - start_time) / 60):.2f} 分钟。")
