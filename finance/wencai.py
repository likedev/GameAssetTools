# -*- coding: utf-8 -*-
import time

import pandas as pd
import akshare as ak
import pymysql
from datetime import datetime, timedelta
import warnings
import pywencai
import stock_db

ck = 'other_uid=Ths_iwencai_Xuangu_ukukt2s9hz6qjynuona9txk5xh5d85sz; ta_random_userid=nt7n2zc4nr; cid=efd8e78112fc993a4a1509237fdbadc11748144707; cid=efd8e78112fc993a4a1509237fdbadc11748144707; ComputerID=efd8e78112fc993a4a1509237fdbadc11748144707; WafStatus=0; user=MDpteF81MzcxNzM3OTI6Ok5vbmU6NTAwOjU0NzE3Mzc5Mjo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjUzNzE3Mzc5MjoxNzUzMDIxNzIyOjo6MTU5NjQxODY4MDoyNjc4NDAwOjA6MTg4YWI2MGUxMTllOTFmOGQwMWRhNjUwZWQwMjUyMTA4OmRlZmF1bHRfNTow; userid=537173792; u_name=mx_537173792; escapename=mx_537173792; ticket=f2e19b8e04b80a100c2180c1e520863b; user_status=0; utk=4b2a9a539d04264405999b849aff38b6; PHPSESSID=d910fafa1b058790e09fb71842b12da9; v=AxqdX_WHJp39dqox6w7I1sbsa8s5S54lEM8SySSTxq14l7T1DNvuNeBfYtj3'

query_condition = '趋势股，3日内未涨停,收盘价小于100，周线周期均线上移，月线周期均线上移，无风险警示,非房地产板块'
sort_param = ''

task_name = '上午盘中'

# 忽略 future warning
warnings.simplefilter(action='ignore', category=FutureWarning)

# ==============================================================================
# 用户配置区域
# ==============================================================================
# MySQL 数据库连接信息
DB_CONFIG = {
    'host': '127.0.0.1',  # 您的数据库地址
    'port': 3306,
    'user': 'root',  # 您的数据库用户名
    'password': 'root',  # 您的数据库密码
    'database': 'stock',  # 您的数据库名称
    'charset': 'utf8mb4'
}


def select_stocks_from_wencai():
    """
    通过 pywencai 筛选股票。
    注意：这里为了演示，我将模拟一个返回结果。
    在实际使用中，您应该取消注释并运行真实的代码。
    """
    print("步骤 1: 正在从问财筛选股票...")
    res = pywencai.get(query=query_condition, sort_order='asc', loop=True, cookie=ck)
    res = res[['股票代码', '股票简称', '所属同花顺行业']]
    print(f"已加载 {len(res)} 只模拟股票。")
    return res


def analyze_and_store_stock_data(stock_list_df):
    """
    分析股票列表中的每只股票，并将结果存入数据库。
    """

    all_stock_df = stock_db.load_all_stock()

    if stock_list_df is None or stock_list_df.empty:
        print("股票列表为空，程序终止。")
        return

    db_conn = pymysql.connect(**DB_CONFIG)
    cursor = db_conn.cursor()

    today_str = datetime.now().strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=150)).strftime('%Y%m%d')  # 获取约5个月的数据

    task_version = today_str + task_name

    # 删除数据表已有的
    cursor.execute(" delete from wencai where 时间 = '%s' " % task_version)
    db_conn.commit()

    for index, row in stock_list_df.iterrows():

        # if index > 3:
        #     break

        stock_code_raw = row['股票代码']
        stock_name = row['股票简称']
        ths_industry = row['所属同花顺行业']

        # 格式化股票代码以适应 akshare
        stock_code_ak = stock_code_raw.split('.')[0]

        print(f"\n处理股票: {stock_name} ({stock_code_ak})")

        try:
            time.sleep(2)

            print("  - 获取历史行情数据...")

            hist_df = ak.stock_zh_a_hist(symbol=stock_code_ak, period="daily", start_date=start_date, end_date=end_date,
                                         adjust="qfq")
            if hist_df.empty or len(hist_df) < 25:  # 确保有足够数据
                print(f"  - 历史数据不足，跳过 {stock_name}")
                continue

            # 获取最新一个交易日的基本面数据
            print("  - 获取最新基本面数据...")
            latest_quote_df = ak.stock_individual_info_em(symbol=stock_code_ak)
            latest_quote = dict(zip(latest_quote_df['item'], latest_quote_df['value']))

            # 准备数据
            hist_df = hist_df.copy()
            hist_df['涨跌幅'] = hist_df['收盘'].pct_change() * 100
            hist_df['振幅'] = (hist_df['最高'] - hist_df['最低']) / hist_df['收盘'].shift(1) * 100

            # 最新一天的数据
            latest_day = hist_df.iloc[-1]

            print(latest_day)

            print("  - 开始计算各项指标...")

            # 行业拆分
            industries = (ths_industry.split('-') + [None, None, None])[:3]

            high_past_7d = hist_df['最高'].rolling(window=7).max().shift(1)
            last_20_closes = hist_df['收盘'].iloc[-20:]
            last_20_past_highs = high_past_7d.iloc[-20:]
            retreat_days_count = (last_20_closes < last_20_past_highs).sum()
            down_days_ratio = retreat_days_count / len(last_20_closes)

            # 十日/五日涨跌比
            last_10_days_chg = hist_df['涨跌幅'].iloc[-10:]
            up_10 = (last_10_days_chg > 0).sum()
            down_10 = (last_10_days_chg < 0).sum()
            ratio_10_day = up_10 / down_10 if down_10 > 0 else up_10

            last_5_days_chg = hist_df['涨跌幅'].iloc[-5:]
            up_5 = (last_5_days_chg > 0).sum()
            down_5 = (last_5_days_chg < 0).sum()
            ratio_5_day = up_5 / down_5 if down_5 > 0 else up_5

            # 最大回撤幅度
            cumulative_max = hist_df['收盘'].cummax()
            drawdown = (hist_df['收盘'] - cumulative_max) / cumulative_max
            drawdown = drawdown.iloc[-30:]
            max_drawdown = abs(drawdown.min()) * 100

            # 上引线概率 (过去两周(10个交易日)，最高价涨幅>3%后，回落超过40%的概率)
            last_14_days = hist_df.iloc[-14:].copy()
            last_14_days['prev_close'] = last_14_days['收盘'].shift(1)
            high_jump_days = last_14_days[
                (last_14_days['最高'] - last_14_days['prev_close']) / last_14_days['prev_close'] > 0.03]
            if not high_jump_days.empty:
                fall_back_days = high_jump_days[(high_jump_days['最高'] - high_jump_days['收盘']) / (
                        high_jump_days['最高'] - high_jump_days['开盘']) > 0.4]
                upper_shadow_prob = len(fall_back_days) / len(high_jump_days)
            else:
                upper_shadow_prob = 0.0

            # 五日平均振幅
            avg_amplitude_5_day = hist_df['振幅'].iloc[-5:].mean()

            # 五日涨幅
            close_5_days_ago = hist_df['收盘'].iloc[-6]
            change_5_day = (latest_day['收盘'] - close_5_days_ago) / close_5_days_ago * 100

            # 红三兵 (过去三天连续上涨，且成交量逐渐放大)
            is_red_three_soldiers = 0
            if len(hist_df) >= 4:
                last_3 = hist_df.iloc[-3:]
                last_4_close = hist_df.iloc[-4]['收盘']
                if (last_3['收盘'] > last_3['开盘']).all() and \
                        (last_3['收盘'].iloc[2] > last_3['收盘'].iloc[1] > last_3['收盘'].iloc[0] > last_4_close) and \
                        (last_3['成交量'].iloc[2] > last_3['成交量'].iloc[1] > last_3['成交量'].iloc[0]):
                    is_red_three_soldiers = 1

            # 高开低走/低开高走 (过去一个月，约22个交易日)
            last_month = hist_df.iloc[-22:].copy()
            last_month['prev_close'] = last_month['收盘'].shift(1)
            high_open_days = last_month[last_month['开盘'] > last_month['prev_close']]
            high_open_low_close_days = high_open_days[high_open_days['收盘'] < high_open_days['开盘']]
            high_open_low_close_prob = len(high_open_low_close_days) / len(
                high_open_days) if not high_open_days.empty else 0.0

            low_open_days = last_month[last_month['开盘'] < last_month['prev_close']]
            if not low_open_days.empty:
                low_open_high_close_days = low_open_days[low_open_days['收盘'] > low_open_days['开盘']]
                low_open_high_close_prob = len(low_open_high_close_days) / len(low_open_days)
            else:
                low_open_high_close_prob = 0.0

            # 均线相关概率
            hist_df['MA5'] = hist_df['收盘'].rolling(window=5).mean()
            last_10_days_ma = hist_df.iloc[-10:]
            touch_ma5_count = ((last_10_days_ma['最低'] <= last_10_days_ma['MA5']) & (
                    last_10_days_ma['最高'] >= last_10_days_ma['MA5'])).sum()
            touch_ma5_prob = touch_ma5_count / 10.0

            last_15_days_ma = hist_df.iloc[-15:]
            close_below_ma5_count = (last_15_days_ma['收盘'] < last_15_days_ma['MA5']).sum()
            close_below_ma5_prob = close_below_ma5_count / 15.0

            # 最近新高
            is_recent_high = 1 if latest_day['收盘'] == hist_df['收盘'].iloc[-5:].max() else 0

            # 得分 (简单示例：形态好加分)
            score = 0
            hist_df['MA20'] = hist_df['收盘'].rolling(window=20).mean()
            hist_df['MA5'] = hist_df['收盘'].rolling(window=5).mean()
            hist_df['MA10'] = hist_df['收盘'].rolling(window=10).mean()
            hist_df['MA60'] = hist_df['收盘'].rolling(window=60).mean()

            if is_red_three_soldiers == 1: score += 3  # 出现红三兵形态

            PE = all_stock_df.loc[stock_code_ak, '市盈率_动态']
            if PE and PE > 0 and PE < 30:
                score += 1

            score += (ratio_10_day if ratio_10_day > 0.4 else 0)
            score += (ratio_5_day if ratio_5_day > 0.3 else 0)

            score -= max_drawdown / 5
            score -= down_days_ratio * 2
            score += change_5_day / 5

            score -= high_open_low_close_prob
            score += low_open_high_close_prob

            score += touch_ma5_prob
            score -= close_below_ma5_prob

            if is_recent_high:
                score += 2

            if latest_day['收盘'] < hist_df['MA5'].iloc[-1]:
                score -= 0.5
                说明 = '收盘 < MA5'

            if all_stock_df.loc[stock_code_ak, '换手率'] > 20:
                score -= 0.5
                说明 = '换手率 > 20'

            if ratio_10_day < 0.4:
                score -= 0.6
                说明 = '十日涨跌比 < 0.4'

            if max_drawdown > 15:
                score -= 0.3
                说明 = '最大回撤幅度 > 15'

            if upper_shadow_prob > 0.5:
                score -= 0.2
                说明 = '上影线概率 > 0.5'

            if high_open_low_close_prob > 0.5:
                score -= 0.1
                说明 = '高开低走概率 > 0.5'

            if all_stock_df.loc[stock_code_ak, '涨跌幅'] > 7.5:
                score -= 0.4
                说明 = '涨幅 > 7.5'

            data_to_insert = {
                '时间': task_version,
                '代码': stock_code_ak,
                '名称': stock_name,
                '最新价': all_stock_df.loc[stock_code_ak, '最新价'],
                '涨跌幅': round(all_stock_df.loc[stock_code_ak, '涨跌幅'], 2),
                '换手率': all_stock_df.loc[stock_code_ak, '换手率'],
                '振幅': all_stock_df.loc[stock_code_ak, '振幅'],
                '量比': all_stock_df.loc[stock_code_ak, '量比'],
                '总市值': float(latest_quote.get('总市值', 0)) / 100000000,  # 转换为亿元
                '流通市值': float(latest_quote.get('流通市值', 0)) / 100000000,  # 转换为亿元
                'PE': PE,
                '行业1': industries[0],
                '行业2': industries[1],
                '行业3': industries[2],
                '得分': score,
                '说明': 说明,
                '十日涨跌比': round(ratio_10_day, 2),
                '五日涨跌比': round(ratio_5_day, 2),
                '最大回撤幅度': round(max_drawdown, 2),
                '上引线概率': round(upper_shadow_prob, 2),
                '下跌天数比': round(down_days_ratio, 2),
                '五日平均振幅': round(avg_amplitude_5_day, 2),
                '五日涨幅': round(change_5_day, 2),
                '红三兵': is_red_three_soldiers,
                '高开低走概率': round(high_open_low_close_prob, 2),
                '低开高走概率': low_open_high_close_prob,
                '触摸五日线概率': round(touch_ma5_prob, 2),
                '五日线下收盘概率': round(close_below_ma5_prob, 2),
                '最近新高': is_recent_high
            }

            # 使用 REPLACE INTO 插入或更新数据
            # REPLACE INTO 会先删除旧记录（如果主键冲突），再插入新记录
            # 这对于每日更新的场景很方便
            cols = ', '.join(f'`{k}`' for k in data_to_insert.keys())
            vals = ', '.join(['%s'] * len(data_to_insert))
            sql = f"REPLACE INTO wencai ({cols}) VALUES ({vals})"

            print(f"  - 准备将数据写入数据库...")
            cursor.execute(sql, tuple(data_to_insert.values()))
            db_conn.commit()
            print(f"  - {stock_name} 数据处理并存储成功。")

        except Exception as e:
            print(f"  - 处理 {stock_name} 时发生错误: {e}")
            db_conn.rollback()  # 如果出错则回滚
            continue

    cursor.close()
    db_conn.close()
    print("\n所有股票处理完毕。")


# ==============================================================================
# 主程序入口
# ==============================================================================
if __name__ == '__main__':
    # 步骤 1: 筛选股票
    selected_stocks = select_stocks_from_wencai()

    # 步骤 2: 分析并存储
    analyze_and_store_stock_data(selected_stocks)
