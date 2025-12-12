import time
from IPython.display import display, Markdown, HTML
import pandas as pd
import stock_db
import akshare as ak
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go # Often needed for more customization
sns.set_style('whitegrid')


def do_stat(wc_df):
    all_stock = stock_db.load_all_stock()
    try:
        price_start = wc_df[['最新价', '得分']].rename(columns={'最新价': 'price_start'})
        price_end = all_stock[['最新价', '名称']].rename(columns={'最新价': 'price_end'})
    except KeyError as e:
        display(Markdown(f"<div class='alert alert-danger'>❌ 列名错误: {e}</div>"))
        return

    merged_df = price_start.join(price_end, how='inner')

    if merged_df.empty:
        display(Markdown("<div class='alert alert-warning'>⚠️ 两个DataFrame中没有共同的股票代码</div>"))
        return

    merged_df.dropna(inplace=True)
    merged_df = merged_df[merged_df['price_start'] > 0]
    merged_df['涨跌幅'] = (merged_df['price_end'] - merged_df['price_start']) / merged_df['price_start']

    # 创建结果摘要
    total_count = len(merged_df)
    avg_change_total = merged_df['涨跌幅'].mean()

    # 1. 显示统计摘要（使用Markdown格式）
    display(Markdown(f"### 📊 选股统计分析 "))
    display(Markdown(f"<div class='summary-box'>"
                     f"<h4 class='section-title'>整体统计</h4>"
                     f"<p>• 共分析股票数: <b>{total_count}</b> 只</p>"
                     f"• 全体平均涨跌幅: <span class={'positive' if avg_change_total >= 0 else 'negative'}>"
                     f"{avg_change_total:.2%}</span></div>"))

    # 2. 前1/3和后1/3分析
    if total_count >= 3:
        one_third_count = total_count // 3
        sorted_df = merged_df.sort_values(by='涨跌幅', ascending=False)
        top_third_df = sorted_df.head(one_third_count)
        bottom_third_df = sorted_df.tail(one_third_count)

        avg_top = top_third_df['涨跌幅'].mean()
        avg_bottom = bottom_third_df['涨跌幅'].mean()

        # 美化表格显示
        def color_positive_negative(val):
            color = 'green' if '-' in val else 'red'
            return f'color: {color}; font-weight: bold'

        # 格式化表格
        top_display = top_third_df[['名称', '涨跌幅']].copy()
        top_display['涨跌幅'] = top_display['涨跌幅'].apply(lambda x: f'{x:.2%}')
        top_display = top_display.rename(columns={
            '名称': '股票名称',
            '涨跌幅': '涨幅'
        })

        bottom_display = bottom_third_df[['名称', '涨跌幅']].copy()
        bottom_display['涨跌幅'] = bottom_display['涨跌幅'].apply(lambda x: f'{x:.2%}')
        bottom_display = bottom_display.rename(columns={
            '名称': '股票名称',
            '涨跌幅': '涨幅'
        })

        # 显示结果
        display(Markdown(f"<div class='summary-box'>"
                         f"<h4 class='section-title'>分组分析</h4>"
                         f"<p>• 前1/3 ({one_third_count}只) 平均涨幅: "
                         f"<span class={'positive' if avg_top >= 0 else 'negative'}>"
                         f"{avg_top:.2%}</span></p>"
                         f"<p>• 后1/3 ({one_third_count}只) 平均涨幅: "
                         f"<span class={'positive' if avg_bottom >= 0 else 'negative'}>"
                         f"{avg_bottom:.2%}</span></p></div>"))

        # 使用并排表格显示
        display(Markdown("### 📈 涨幅前1/3股票"))
        display(top_display.style.applymap(color_positive_negative, subset=['涨幅'])
        .set_properties(**{'text-align': 'center'})
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#3498db'), ('color', 'white')]
        }]))

        display(Markdown("### 📉 涨幅后1/3股票"))
        display(bottom_display.style.applymap(color_positive_negative, subset=['涨幅'])
        .set_properties(**{'text-align': 'center'})
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#3498db'), ('color', 'white')]
        }]))
    else:
        display(Markdown("<div class='alert alert-info'>ℹ️ 共同股票数量不足3只，无法进行分组分析</div>"))

    # 3. 添加可视化图表
    if not merged_df.empty:
        display(Markdown("### 📊 涨跌幅分布直方图 (Price Change Distribution Histogram)"))

        # Create an interactive histogram with Plotly Express
        fig = px.histogram(
            merged_df,
            x='涨跌幅',
            nbins=20,
            histnorm='probability density',  # Use this for a proper KDE overlay
            marginal='rug',  # Adds a rug plot for individual data points
            color_discrete_sequence=['skyblue'],
            title='<b>股票涨跌幅分布 (Stock Price Change Distribution)</b>'
        )

        # Add the vertical line for the average
        fig.add_vline(
            x=avg_change_total,
            line_color='red',
            line_dash='dash',
            annotation_text=f'平均值 (Average): {avg_change_total:.2%}',
            annotation_position='top right'
        )

        # Update layout for better readability and to match original labels
        fig.update_layout(
            xaxis_title='涨跌幅 (Price Change %)',
            yaxis_title='密度 (Density)',  # Changed from '股票数量' to '密度' to match histnorm
            bargap=0.1,  # Gap between bars
            legend_title_text='图例 (Legend)'
        )
        fig.show()
