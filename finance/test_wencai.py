import time

import stock_db
import akshare as ak

Test_Wencai = "2025-07-30晚选"

wencai_df = stock_db.select_wencai(" select * from wencai where 时间 = '%s' " % Test_Wencai)

all_stock = stock_db.load_all_stock()


def do_stat(wc_df):
    try:
        price_start = wc_df[['最新价', '得分']].rename(columns={'最新价': 'price_start'})
        price_end = all_stock[['最新价', '名称']].rename(columns={'最新价': 'price_end'})
    except KeyError as e:
        print(f"列名错误: {e}。请检查并修改 WC_PRICE_COL 或 ALL_STOCK_PRICE_COL 的值。")
        # 如果列名错误，则退出
        exit()

    # 使用 'inner' join 合并，只保留共有的股票
    # 索引都是'代码'，所以可以直接join
    merged_df = price_start.join(price_end, how='inner')
    # 2. 数据清洗和计算涨跌幅
    if merged_df.empty:
        print("两个DataFrame中没有共同的股票代码，无法进行计算。")
    else:
        # 删除任何可能存在的缺失值
        merged_df.dropna(inplace=True)

        # 过滤掉起始价格为0或负数的数据，防止计算错误 (division by zero)
        merged_df = merged_df[merged_df['price_start'] > 0]

        # 计算涨跌幅
        merged_df['涨跌幅'] = (merged_df['price_end'] - merged_df['price_start']) / merged_df['price_start']

        # 3. 统计分析
        print(f"共有 {len(merged_df)} 只股票在两个数据源中都存在，并参与计算。")
        print("-" * 50)

        # 计算总平均涨跌幅
        avg_change_total = merged_df['涨跌幅'].mean()
        print(f"全体平均涨跌幅: {avg_change_total:.2%}")

        # 按涨跌幅降序排列
        sorted_df = merged_df.sort_values(by='涨跌幅', ascending=False)

        # 计算前 1/3 和后 1/3
        num_stocks = len(sorted_df)
        if num_stocks >= 3:
            one_third_count = num_stocks // 3

            # 取出前 1/3 (涨幅最高)
            top_third_df = sorted_df.head(one_third_count)

            # 取出后 1/3 (涨幅最低/跌幅最大)
            bottom_third_df = sorted_df.tail(one_third_count)

            # 分别计算平均值
            avg_change_top_third = top_third_df['涨跌幅'].mean()
            avg_change_bottom_third = bottom_third_df['涨跌幅'].mean()

            print(f"涨幅前 1/3 ({one_third_count}只) 的平均涨幅: {avg_change_top_third:.2%}")
            print(f"涨幅后 1/3 ({one_third_count}只) 的平均涨跌幅: {avg_change_bottom_third:.2%}")

            top_third_df['增长率_展示'] = top_third_df['涨跌幅'].map('{:.1%}'.format)
            bottom_third_df['增长率_展示'] = bottom_third_df['涨跌幅'].map('{:.1%}'.format)

            # (可选) 显示涨幅最高和最低的股票详情
            print("\n--- 涨幅前 1/3 股票详情 ---")
            print(top_third_df[['名称', '增长率_展示']])
            print("\n--- 涨幅后 1/3 股票详情 ---")
            print(bottom_third_df[['名称', '增长率_展示']])

        else:
            print("共同股票数量不足3只，无法进行 1/3 切片分析。")


do_stat(wencai_df[wencai_df['得分'] < 0])
