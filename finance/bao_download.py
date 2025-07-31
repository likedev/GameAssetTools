import baostock as bs
import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import time

# --- 数据库配置 ---
# 请根据您的MySQL服务器信息修改以下配置
DB_CONFIG = {
    'user': 'root',  # 数据库用户名
    'password': 'root',  # 数据库密码
    'host': 'localhost',  # 数据库主机
    'port': 3306,  # 数据库端口
    'database': 'stock'  # 您创建的数据库名称
}

# --- 全局变量 ---
TABLE_NAME = 'bs_stock_historical_data'

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


def get_all_stocks_on_date(trade_date):
    """获取指定交易日的所有A股列表"""
    print(f"正在获取 {trade_date} 的股票列表...")
    stock_rs = bs.query_all_stock(day=trade_date)
    stock_df = stock_rs.get_data()
    # 筛选出沪深A股（sh或sz开头），且非ST、非退市
    stock_df = stock_df[(stock_df['code'].str.match(r'^(sh|sz)\.6')) | (stock_df['code'].str.match(r'^(sh|sz)\.[03]'))]
    stock_df = stock_df[stock_df['tradeStatus'] == '1']  # 筛选交易状态为1（正常交易）的
    print(f"获取到 {len(stock_df)} 支正常交易的A股。")
    return stock_df['code'].tolist()


def store_historical_data():
    """
    获取并存储所有A股近3年的前复权历史数据。
    此函数为增量更新，只会获取数据库中缺失的数据。
    """
    print("\n--- 开始登录 Baostock ---")
    lg = bs.login()
    if lg.error_code != '0':
        print(f"Baostock 登录失败: {lg.error_msg}")
        return

    try:
        # 1. 确定需要获取数据的时间范围
        end_date = datetime.date.today().strftime('%Y-%m-%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=3 * 365)).strftime('%Y-%m-%d')

        # 2. 获取最新一个交易日的所有股票代码
        # Baostock 需要一个具体的日期来获取股票列表
        latest_trade_date_rs = bs.query_trade_dates(end_date=end_date)
        latest_trade_date = latest_trade_date_rs.get_data().iloc[0]['calendar_date']
        all_stock_codes = get_all_stocks_on_date(latest_trade_date)

        # 3. 定义要查询的字段
        fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"

        # 4. 遍历每支股票，获取并存储历史数据
        total = len(all_stock_codes)
        for i, stock_code in enumerate(all_stock_codes):

            # 增量更新逻辑：检查该股票的最新日期，从下一天开始获取
            update_start_date = start_date
            try:
                with engine.connect() as connection:
                    query = text(f"SELECT MAX(`date`) FROM {TABLE_NAME} WHERE `code` = '{stock_code}'")
                    last_date = connection.execute(query).scalar()

                if last_date:
                    update_start_date = (last_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    print(
                        f"[{i + 1}/{total}] {stock_code}: 数据库中最新数据为 {last_date.strftime('%Y-%m-%d')}，将从 {update_start_date} 开始更新。")
                else:
                    print(f"[{i + 1}/{total}] {stock_code}: 数据库无历史数据，将获取最近3年数据。")
            except Exception as e:
                print(f"[{i + 1}/{total}] {stock_code}: 查询最新日期失败（可能是新表），将获取最近3年数据。")

            if update_start_date > end_date:
                print(f"[{i + 1}/{total}] {stock_code}: 数据已是最新，无需更新。")
                continue

            # 获取前复权（adjustflag=2）历史数据
            rs = bs.query_history_k_data_plus(
                stock_code, fields,
                start_date=update_start_date, end_date=end_date,
                frequency="d", adjustflag="2"
            )

            if rs.error_code != '0':
                print(f"获取 {stock_code} 数据失败: {rs.error_msg}")
                continue

            result_df = rs.get_data()
            if result_df.empty:
                continue

            # 数据清洗：将空字符串替换为 None，并转换数据类型
            result_df.replace('', pd.NA, inplace=True)
            numeric_cols = ['open', 'high', 'low', 'close', 'preclose', 'volume', 'amount',
                            'turn', 'pctChg', 'peTTM', 'pbMRQ', 'psTTM', 'pcfNcfTTM']
            for col in numeric_cols:
                result_df[col] = pd.to_numeric(result_df[col], errors='coerce')

            # 存入数据库
            try:
                result_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
                print(f"[{i + 1}/{total}] 成功存储 {stock_code} 的 {len(result_df)} 条历史数据。")
            except Exception as e:
                print(f"[{i + 1}/{total}] 存储 {stock_code} 数据时出错: {e}")

            # 礼貌地暂停一下，避免对服务器造成过大压力
            time.sleep(0.1)

    finally:
        bs.logout()
        print("\n--- Baostock 已登出，任务结束 ---")


# --- 主程序入口 ---
if __name__ == "__main__":
    store_historical_data()
