import pandas as pd
from tabulate import tabulate


def cal_price(price0, reduce_p, add_money, double_=-1):
    price_today = price0
    invest0 = 10000.0
    invest = invest0
    stock = invest / price_today

    res_arr = []
    df = pd.DataFrame()
    for i in range(1, 7):
        price_today = price_today * (1 + reduce_p)

        today_add_money = -1
        if double_ > 0:
            today_add_money = invest0 * pow(double_, i - 1)
        else:
            today_add_money = add_money  # 总投资
        invest = invest + today_add_money
        stock = stock + today_add_money / price_today  # 股票数

        cost_avg = invest / stock  # 平均成本

        today_value = price_today * stock

        loss_p = (invest - today_value) / invest
        huiben_p = (invest - today_value) / today_value

        result = {}

        result["股数"] = round(stock)
        result["今日价格"] = round(price_today, 2)
        result["平均成本"] = round(cost_avg, 2)

        result["总市值"] = round(today_value, 2)

        result["损失比例"] = str(round(loss_p * 100, 2)) + '%'
        result["总投入"] = invest
        result["股价跌了xxx"] = str(round((price_today - price0) * 100 / price0, 2)) + '%'
        result["涨xx回本"] = str(round(huiben_p * 100, 2)) + '%'

        res_arr.append(result)

    df = pd.DataFrame(res_arr)
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    df.to_html(r"F:\tmp\stock_result.html")


cal_price(25.0, -0.10, 10000.0, 2.0)
