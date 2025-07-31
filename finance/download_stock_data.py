import akshare as ak
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import time
import adata
import pandas as pd
import numpy as np
# adata.proxy(is_proxy=True, ip='127.0.0.1:7890')

#
# import os
#
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
# os.environ['https_proxy'] = 'http://127.0.0.1:7890'

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
try:
    engine = create_engine(
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    print("数据库连接成功！")
except Exception as e:
    print(f"数据库连接失败：{e}")
    exit()


# --- 函数定义 ---


def store_daily_snapshot():
    """
    获取A股所有股票的当日行情快照，并存入 stock_daily_info 表。
    如果当天数据已存在，则会跳过。
    """
    table_name = 'stock'
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    print(f"\n--- 开始处理 {today_str} 的每日行情快照 ---")

    print("正在通过 akshare 获取A股所有股票的实时行情...")
    try:
        # 获取数据
        stock_spot_df = ak.stock_zh_a_spot_em()
        if stock_spot_df.empty:
            print("未能获取到行情数据，可能是非交易日或API问题。")
            return

        print(f"成功获取 {len(stock_spot_df)} 条股票行情数据。")

        # 数据清洗和整理
        # 1. 为了数据库存储，重命名字段中的特殊字符
        stock_spot_df.rename(columns={'市盈率-动态': '市盈率_动态'}, inplace=True)
        # 2. 增加一个记录日期列
        stock_spot_df['记录日期'] = pd.to_datetime(today_str)

        # 3. 筛选出建表语句中定义的列，避免因akshare接口列变动导致出错
        required_columns = [
            '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额',
            '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率',
            '市盈率_动态', '市净率', '总市值', '流通市值', '记录日期'
        ]
        # 过滤掉不存在于DataFrame中的列
        existing_columns = [col for col in required_columns if col in stock_spot_df.columns]
        df_to_save = stock_spot_df[existing_columns]

        # 存入数据库
        print(f"正在将数据写入数据库表 '{table_name}'...")
        df_to_save.to_sql(table_name, engine, if_exists='replace', index=False)
        print("每日行情快照数据存储成功！")

    except Exception as e:
        print(f"处理每日行情快照时发生错误: {e}")


def store_historical_data():
    """
    获取所有A股近3年的前复权历史数据，并存入 stock_historical_price 表。
    此函数为增量更新，只会获取缺失的数据。
    """
    table_name = 'stock'
    print(f"\n--- 开始处理历史K线数据（最近3年） ---")

    # 1. 获取所有A股代码列表
    try:
        stock_list_df = ak.stock_zh_a_spot_em()[['代码', '名称']]
        print(f"获取到 {len(stock_list_df)} 支A股股票。")
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return

    # 2. 确定需要获取数据的时间范围
    end_date = datetime.date.today().strftime('%Y%m%d')
    end_date = datetime.date.today().strftime('2025-07-04')
    start_date = (datetime.date.today() - datetime.timedelta(days=3 * 365)).strftime('%Y%m%d')

    # 3. 遍历每支股票，获取并存储历史数据
    total = len(stock_list_df)
    for index, row in stock_list_df.iterrows():
        stock_code = row['代码']
        stock_name = row['名称']

        # 增量更新逻辑：检查该股票的最新日期，从下一天开始获取
        update_start_date = start_date
        try:
            with engine.connect() as connection:
                query = text(f"SELECT MAX(`日期`) FROM {table_name} WHERE `代码` = '{stock_code}'")
                last_date = connection.execute(query).scalar()

            if last_date:
                update_start_date = (last_date + datetime.timedelta(days=1)).strftime('%Y%m%d')
                print(
                    f"[{index + 1}/{total}] {stock_code} {stock_name}: 数据库中最新数据为 {last_date.strftime('%Y-%m-%d')}，将从 {update_start_date} 开始更新。")
            else:
                print(f"[{index + 1}/{total}] {stock_code} {stock_name}: 数据库无历史数据，将获取最近3年数据。")
        except Exception as e:
            # 如果查询出错（例如表第一次创建），则从头开始获取
            print(f"[{index + 1}/{total}] {stock_code} {stock_name}: 查询最新日期失败（可能是新表），将获取最近3年数据。")

        if update_start_date > end_date:
            print(f"[{index + 1}/{total}] {stock_code} {stock_name}: 数据已是最新，无需更新。")
            continue

        try:
            # 礼貌地暂停一下，避免对服务器造成过大压力
            time.sleep(2)

            # 使用新的 adata 接口获取日K线数据
            res_df = adata.stock.market.get_market(stock_code=stock_code, k_type=1, start_date=update_start_date)

            # 检查是否成功获取数据
            if res_df.empty:
                print(f"未能获取到 {stock_code} {stock_name} 的历史数据。")
                continue

            # --- 数据转换与计算 (在原始 DataFrame 上一次性完成) ---

            # 1. 计算 "振幅"
            # 使用 .loc 确保我们在原始 DataFrame 上操作
            # 同时，为了避免除以0的情况，我们先将 pre_close 为0或NaN的值替换为一个非零值（如NaN），计算后再处理
            pre_close_safe = res_df['pre_close'].replace(0, np.nan)
            amplitude = ((res_df['high'] - res_df['low']) / pre_close_safe * 100)

            # 将计算结果赋给新列，并填充可能产生的 NaN 值
            res_df['振幅'] = amplitude.fillna(0).round(4)

            # 2. 格式化日期列
            # 直接在 res_df 上完成转换
            res_df['trade_date'] = pd.to_datetime(res_df['trade_date']).dt.date

            # --- 列名对齐和筛选 ---

            # 3. 定义列名映射关系
            column_mapping = {
                'stock_code': '代码',
                'trade_date': '日期',
                'open': '开盘',
                'close': '收盘',
                'high': '最高',
                'low': '最低',
                'volume': '成交量',
                'amount': '成交额',
                # '振幅' 列已在上面创建并赋值
                'change_pct': '涨跌幅',
                'change': '涨跌额',
                'turnover_ratio': '换手率'
            }

            # 4. 重命名列
            res_df.rename(columns=column_mapping, inplace=True)

            # 5. 定义最终需要的列，并按此顺序筛选，创建最终的 DataFrame
            # 此时 hist_df 是一个全新的 DataFrame，后续操作不会再有警告
            target_columns = [
                '代码', '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额',
                '振幅', '涨跌幅', '涨跌额', '换手率'
            ]
            hist_df = res_df[target_columns]

            # 存入数据库
            hist_df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"[{index + 1}/{total}] 成功存储 {stock_code} {stock_name} 的 {len(hist_df)} 条历史数据。")


        except Exception as e:
            print(f"处理 {stock_code} {stock_name} 时发生错误: {e}")

    print("所有股票历史数据处理完毕！")


# --- 主程序入口 ---
if __name__ == "__main__":
    store_daily_snapshot()

    # # 2. 存储或更新历史K线数据
    # # 注意：首次运行此函数会非常耗时，因为它需要下载所有股票近3年的数据。
    # # 后续运行时，它只会增量更新，速度会快很多。
    # store_historical_data()
