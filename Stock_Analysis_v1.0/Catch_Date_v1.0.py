#!/usr/bin/env python
# -*- coding=utf-8 -*-
# --> author: Yu.Zhang
# --> architect: XiaoYong.Gao
# --> China University of Petroleum, Beijing
# --> time: 2021/6/2

#调库
import pandas as pd
import time
import akshare as ak
import tushare as ts
import pymysql
from sqlalchemy import create_engine, types
import re
import json
import urllib.request
import matplotlib.pyplot as plt
from typing import List, Union
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
import webbrowser as wb
import wx
import win32api
import sys


'''---------------------------------------第一步：获取期货数据 fuction-AKshare ------------------------------------------'''
'''=============================================实时数据获取:fuction==================================================='''
# 实时股票行情数据（非交易时段无法保证正常获取）  --非项目需--

def realtime_data():
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    print(stock_zh_a_spot_df)

# 内盘-实时行情数据（来源新浪）(problem：不在交易时间内无法获取，error)    --项目需求--

def inside_realtime_data():
    '''获取上期能源中的原油实时数据'''
    dce_text = ak.match_main_contract(exchange="dce")
    czce_text = ak.match_main_contract(exchange="czce")
    shfe_text = ak.match_main_contract(exchange="shfe")
   # ine_text  = ak.match_main_contract(exchange="ine")
    while True:
        time.sleep(3)
        data = ak.futures_zh_spot(
            subscribe_list=",".join([dce_text, czce_text, shfe_text]),
            market="CF")
        print(data)
        data.to_csv('inside_realtime_data')

# 外盘-实时行情数据（源新浪：https://finance.sina.com.cn/futuremarket/）提供新浪财经-期货页面的外盘实时行情数据，单次返回当日可以订阅的所有期货品种数据

"""//-->This function outside_realtime_data works fine.<--//"""
def outside_realtime_data():
    print("开始接收实时行情, 每秒刷新一次")
    subscribe_list = ak.hq_subscribe_exchange_symbol()
    while True:
        time.sleep(3)
        futures_hq_spot_df = ak.futures_hq_spot(subscribe_list=subscribe_list)
        print(futures_hq_spot_df)

'''========================================= 获取发行日到最近交易日的历史数据:fuction ====================================='''
# 内盘-历史行情数据（新浪）

def inside_history_data():      # 由于爬取的是整个时间段的历史数据，其中会有非交易日存在，故获取速度较慢
    '''
    '可获取：上期能源的原油数据如下'
    {
      [期货名称  :  期货代码]
      '上海原油连续 '：sc0
      '上海原油2107': sc2107
      '上海原油2108': sc2108
      '上海原油2109': sc2109
      '上海原油2110': sc2110
      '上海原油2112': sc2112
      '上海原油2111': sc2111
      '上海原油2201': sc2201
      '上海原油2406': sc2406
    }
    {
      Market:
      'CFFEX' = '中金所'
      'INE'   = '上期能源'
      'CZCE'  = '郑商所'
      'SHFE'  = '上期所'
      'DCE'   = '大商所'
    }
    :return:
    '''
    get_futures_daily_df = ak.get_futures_daily(start_date="20200701", end_date="20210601",market="INE", index_bar=True)   # market = ['CFFEX'='中金所','INE'='上期能源','CZCE'='郑商所','SHFE'='上期所','DCE'='大商所'] index_bar：是否合成指数
    # 上述代码可指定日期start_date和end_date

    print(get_futures_daily_df)
    get_futures_daily_df.to_csv('inside_history_data.csv')

# 外盘-历史行情数据（来源新浪）

"""//-->This function outside_history_data works fine.<--//"""
def outside_history_data():
    futures_foreign_hist_df = ak.futures_foreign_hist(symbol="NG")     # 布伦特原油CFD（OIL）、纽约原油（CL）、NYMEX天然气（NG）
    """
    '可获取：布伦特原油CFD（OIL）、纽约原油（CL）、NYMEX天然气（NG）的历史数据'
    """
    print(futures_foreign_hist_df)
    # futures_foreign_hist_df.to_csv('futures_fh_df.csv')

## 外盘-布伦特原油CFD（OIL）历史行情数据

def outside_history_brent_oil_data():
    futures_foreign_hist_df = ak.futures_foreign_hist(symbol="OIL")
    print(futures_foreign_hist_df)

    return futures_foreign_hist_df

## 外盘-纽约原油（CL）历史行情数据

def outside_history_newyork_oil_data():
    futures_foreign_hist_df = ak.futures_foreign_hist(symbol="CL")
    print(futures_foreign_hist_df)

    return futures_foreign_hist_df

## 外盘-NYMEX天然气（NG）历史行情数据

def outside_history_newyork_natural_gas_data():
    futures_foreign_hist_df = ak.futures_foreign_hist(symbol="NG")
    print(futures_foreign_hist_df)

    return futures_foreign_hist_df

# 全球商品期货

def global_commodity_futures():
    '''
    {能源包括以下：
    '伦敦布伦特原油': '/commodities/brent-oil',
        'WTI原油': '/commodities/crude-oil',
        '伦敦汽油': '/commodities/london-gas-oil',
        '天然气': '/commodities/natural-gas',
        '燃料油': '/commodities/heating-oil',
        '碳排放': '/commodities/carbon-emissions',
        'RBOB汽油': '/commodities/gasoline-rbob',
        '布伦特原油': '/commodities/brent-oil',
        '原油': '/commodities/crude-oil'
    :return:
    '''
    # --------下为测试代码-------------
    # futures_global_commodity_name_url_map_dict = ak.futures_global_commodity_name_url_map(sector="能源")
    # print(futures_global_commodity_name_url_map_dict)
    # --------^为测试代码-------------

    futures_global_commodity_hist_df = ak.futures_global_commodity_hist(sector="能源", symbol="原油")    # 可设置symbol参数之间调用爬取指定能源数据
    print(futures_global_commodity_hist_df)


"""===========================================国内A股三大指数（上证、深证、科创版）========================================="""

# 上证-股票市场总貌

def SH_stock_situation():
    '''上海证券交易所-股票数据总貌,单次返回最近交易日的股票数据总貌数据(当前交易日的数据需要交易所收盘后统计)'''
    stock_sse_summary_df = ak.stock_sse_summary()
    print(stock_sse_summary_df)

# 深证所-股票市场

def SZ_stock_situation():
    '''深圳证券交易所-市场总貌,单次返回最近交易日的市场总貌数据(当前交易日的数据需要交易所收盘后统计)'''
    stock_szse_summary_df = ak.stock_szse_summary(date="20210601")   # date="20200619"; 当前交易日的数据需要交易所收盘后统计  可引入一个变量如：date = today 为输入的参数
    print(stock_szse_summary_df)

# 上交所-每日概况

def SH_market_daily_situation():
    '''上海证券交易所-数据-股票数据-成交概况-股票成交概况-每日股票情况,单次返回指定日期的每日概况数据, 当前交易日数据需要在收盘后获取'''
    stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date="20201111")   # date="20200619"; 当前交易日的数据需要交易所收盘后统计  可引入一个变量如：date = today 为输入的参数
    print(stock_sse_deal_daily_df)

# 实时行情数据  -- 根据项目需求貌似用不上（*。*）--

def Realtime_market_situation():
    '''
    A 股数据是从新浪财经获取的数据, 重复运行本函数会被新浪暂时封 IP, 建议增加时间间隔
    单次返回所有 A 股上市公司的实时行情数据
    '''
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    print(stock_zh_a_spot_df)

# 历史行情数据 -- 根据项目需求貌似也用不上（*。*）--

def History_market_situation():
    '''
    A 股数据是从新浪财经获取的数据, 历史数据按日频率更新; 注意其中的 sh689009 为 CDR, 请 通过 stock_zh_a_cdr_daily 接口获取
    单次返回指定 A 股上市公司指定日期间的历史行情日频率数据
    :return:
    '''
    stock_zh_a_daily_qfq_df = ak.stock_zh_a_daily(symbol="sz000002", start_date="20101103", end_date="20201116",
                                                  adjust="qfq")

    # symbol='sh600000'; 股票代码可以在 ak.stock_zh_a_spot() 中获取
    # start_date='20201103'; 开始查询的日期
    # end_date='20201116'; 结束查询的日期
    # 默认返回不复权的数据; qfq: 返回前复权后的数据; hfq: 返回后复权后的数据; hfq-factor: 返回后复权因子; qfq-factor: 返回前复权因子

    print(stock_zh_a_daily_qfq_df)


# 实时行情指数（上证、深证等）   --项目需求--

def Realtime_Market_Index():
    '''
    中国股票指数数据, 注意该股票指数指新浪提供的国内股票指数
    单次返回所有指数的实时行情数据
    :return:
    '''
    stock_zh_index_spot_df = ak.stock_zh_index_spot()
    print(stock_zh_index_spot_df)

# 历史行情指数-新浪      --项目需求--（可指定上证、深证指数）

def History_Market_Index_xinlang():
    '''股票指数数据是从新浪财经获取的数据, 历史数据按日频率更新'''

    stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol="sz399552")       # 新浪的数据开始时间, 不是证券上市时间
    print(stock_zh_index_daily_df)


# 科创板-实时行情指数   --项目需求--

def Sci_Tech_Broad_Realtime_Index():
    '''
    从新浪财经获取科创板股票数据
    单次返回所有科创板上市公司的实时行情数据
    '''
    stock_zh_kcb_spot_df = ak.stock_zh_kcb_spot()
    print(stock_zh_kcb_spot_df)

# ------------tushare fuction-----------------
# 指数基本信息
def tu_index_basic():
    ''''''
    pro = ts.pro_api('d6f360252b4fb3e2b7894ba077c4e29a154600c56637784cec60e2e9')

    df = pro.index_basic(market='SSE')   # 上交所指数-SSE  深交所指数-SZSE 	MSCI指数-MSCI
    print(df)

# 指数日线行情   --貌似无用
def tu_index_daily_situation():      # --无法获取上证指数
    '''获取指数每日行情，还可以通过bar接口获取。由于服务器压力，目前规则是单次调取最多取8000行记录，可以设置start和end日期补全。指数行情也可以通过通用行情接口获取数据．'''
    pro = ts.pro_api('d6f360252b4fb3e2b7894ba077c4e29a154600c56637784cec60e2e9')

    df1 = pro.index_daily(ts_code='399300.SZ')     # ts_code=获取你需要的指数代码，这里的000001.SZ=上证指数，000002.SH=上证A指，000003.SH=上证B指
    print(df1)
    # 或者按日期取

    df2 = pro.index_daily(ts_code='000002.SZ', start_date='20180101', end_date='20181010')
    print(df2)



"""======================================================汇率价格======================================================"""

# 货币报价最新数据

def Currency_New_Price():
    '''
    获取货币报价最新数据
    单次返回指定货币的最新报价数据-免费账号每月限量访问 5000 次  从 https://currencyscoop.com/获取 api_key
    :return:
    '''
    currency_latest_df = ak.currency_latest(base="USD", api_key="9eb19ec0bfe3eebc0fc54992b23873f7")     # 需要在这里获取api的字符串才能访问
    print(currency_latest_df)

# 货币报价历史数据

def Currency_History_Price():
    '''
    获取货币报价历史数据
    单次返回指定货币在指定交易日的报价历史数据-免费账号每月限量访问 5000 次
    :return:
    '''
    currency_history_df = ak.currency_history(base="USD", date="2020-02-03", api_key="9eb19ec0bfe3eebc0fc54992b23873f7")     # 需要在这里获取api的字符串才能访问
    print(currency_history_df)

# 货币基础信息查询   --用处不大--

def Currency_Exchange_Information():
    currency_currencies_df = ak.currency_currencies(c_type="fiat", api_key="9eb19ec0bfe3eebc0fc54992b23873f7")
    print(currency_currencies_df)

# 货币对价格转换

def Currency_Exchange_Price():
    '''
    获取指定货币对指定货币数量的转换后价格
    单次返回指定货币对的转换后价格-免费账号每月限量访问 5000 次
    '''
    currency_convert_se = ak.currency_convert(base="USD", to="CNY", amount="10000",
                                              api_key="9eb19ec0bfe3eebc0fc54992b23873f7")    # 需要在这里获取api的字符串才能访问，api_key="Please put your api key here"; you can register currencyscoop, Gmail well be better
    print(currency_convert_se)

# 人名币兑换美元  --项目需求--

def RMB_Covert_USD():
    currency_convert_se = ak.currency_convert(base="USD", to="CNY", amount="10000",     # 需要在这里获取api的字符串才能访问
                                              api_key="9eb19ec0bfe3eebc0fc54992b23873f7")
    print(currency_convert_se)

# 人名币兑换英镑  --项目需求--

def RMB_Covert_GBP():
    currency_convert_se = ak.currency_convert(base="GBP", to="CNY", amount="10000",
                                              api_key="9eb19ec0bfe3eebc0fc54992b23873f7")       # 需要在这里获取api的字符串才能访问
    print(currency_convert_se)

# 汇率价格-人名币兑美元、人名币兑英镑（来源新浪）   --项目需求--可实现

def Covert_RMB_Realtime():
    '''
    获取人民币外汇即期报价
    单次返回实时行情数据
    :return:
    '''
    fx_df = ak.fx_spot_quote()
    print(fx_df)

# 无api版本汇率实时兑换--RMB：USD    --简洁版--

def Exchange_Rate_Realtime_By_self(url_choose, currency_name):             # 自定义函数 url_choose = http://webforex.hermes.hexun.com/forex/quotelist?code=FOREXUSDCNY&column=Code,Price 为美元价格
    '''
    url_choose = "http://webforex.hermes.hexun.com/forex/quotelist?code=FOREXUSDCNY&column=Code,Price" 为美元价格
    url_choose = "http://webforex.hermes.hexun.com/forex/quotelist?code=FOREXGBPCNY&column=Code,Price" 为英镑价格
    '''
    # 验证请求信息
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}

    # 爬取实时美元汇率数据
    chaper_url = url_choose
    req = urllib.request.Request(url=chaper_url, headers=headers)
    f = urllib.request.urlopen(req)
    html = f.read().decode("utf-8")
    print(html)

    s = re.findall("{.*}", str(html))[0]
    sjson = json.loads(s)

    USDCNY = sjson["Data"][0][0][1] / 10000
    print('实时%r价格: %r' % (currency_name, USDCNY))

"""=========================================== =======新闻资讯(附加扩展属性)============================================="""

# 金十数据-实时资讯  --可访问--

def Js_world_realtime_news():
    '''获取金十数据新闻资讯数据,当日最近 4 小时内的新闻资讯数据'''
    js_news_df = ak.js_news(indicator='最新资讯')
    print(js_news_df)

# 个股新闻  --可访问--

def one_stock_news():
    '''获取东方财富指定个股的新闻资讯数据,当日最近 20 条新闻资讯数据'''
    stock_news_em_df = ak.stock_news_em(stock="601015")
    print(stock_news_em_df)

# 阿尔戈斯全网监控   --不能访问--

def argus_world_watch():
    '''
    获取期货, 股票, 期权, 大宗商品、外汇等价格波动及相关资讯
    发起请求后返回数据, 注意访问频率, 此接口的目标网站稳定性较差, 可能造成部分时间段无法访问
    '''
    watch_argus_df = ak.watch_argus()
    print(watch_argus_df)


'''-----------------------------------------------第二步：存储数据到MySQL-----------------------------------------------'''
# 连接数据库   --test version--
def connect_mysql():
    '''创建数据库的连接引擎'''

    print('连接到MySQL服务器...')
    time.sleep(2)  # 初始化，等待2second
    print('...')
    con = create_engine('mysql+pymysql://root:970804@localhost:3306/stock_finance?charset=utf8')    # 'root'代表本地数据库的名称，冒号后面的’number‘代表的是进入数据库的密码，端口号为：3306/数据库的名称？charset代表字符类别
    time.sleep(1)
    print('...'
          '\nMySQL连接成功！')
    # if con==True:
    #     print('MySQL连接成功！')
    # else:
    #     pass
    return con

'''----------------------------------------------第三步：可视化（进阶）--------------------------------------------------'''
# 引入pyechart->html实现可视化

# 获取json数据 --trouble
def get_data():
    '''DataFrame转json，默认的orient是’columns’，orient可选参数有 {‘split’,’records’,’index’,’columns’,’values’}'''
    # -test- 将外盘布伦特原油数据转换成json格式
    json_response=outside_history_brent_oil_data().to_json(orient='columns')
    print(json_response)

    return split_data(json_response)

# 分离数据   --trouble
def split_data(data):
    category_data = []
    values = []
    volumes = []

    for i, tick in enumerate(data):
        category_data.append(tick[0])
        values.append(tick)
        volumes.append([i, tick[4], 1 if tick[1] > tick[2] else -1])
    return {"categoryData": category_data, "values": values, "volumes": volumes}

# 移动平均数计算
def moving_average(data, day_count):
    data = data.values[:, 0]
    result = []
    for i in range(len(data)):
        start_day_index = i - day_count + 1
        if start_day_index <= 0:
            start_day_index = 0
        justified_day_count = i - start_day_index + 1
        mean = data[start_day_index:i + 1].sum() / justified_day_count
        result.append(mean)
    return result

# k线             --项目需求：已实现--
def show_kline():
    # 读取.csv文件，
    stock_code = 'Brent_OIL'

    stock_data = pd.read_csv('外盘-布伦特原油历史数据.csv', encoding='gb2312')
    # 将文件内容按照by=[‘date’]内容进行排序
    stock_data = stock_data.sort_values(by=["date"], ascending=[True], inplace=False)

    stock_data_cleared = stock_data[stock_data['close'] > 0]

    stock_name = stock_data_cleared["position"][0]

    stock_data_extracted = stock_data_cleared[["open", "close", "low", "high", "volume", "date"]]

    kline = (
        Kline()
            .add_xaxis(stock_data_extracted["date"].values.tolist())
            .add_yaxis("K线图", stock_data_extracted.iloc[:, :4].values.tolist())
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True, is_show=False),
            # axis_opts=opts.AxisOpts(is_scale=True,min_=0), #y轴起始坐标可以设为0
            yaxis_opts=opts.AxisOpts(is_scale=True),  # y轴起始坐标可自动调整
            #title_opts=opts.TitleOpts(title="价格", subtitle=stock_name + "\n" + stock_code, pos_top="20%"),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            datazoom_opts=[  # 设置zoom参数后即可缩放
                opts.DataZoomOpts(
                    is_show=True,
                    type_="inside",
                    xaxis_index=[0, 1],  # 设置第0轴和第1轴同时缩放
                    range_start=0,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="90%",
                    range_start=0,
                    range_end=100,
                ),
            ],

        )
    )

    # 移动平均线
    line = (
        Line()
            .add_xaxis(xaxis_data=stock_data_extracted["date"].values.tolist())
            .add_yaxis(
            series_name="MA5",
            y_axis=moving_average(stock_data_extracted[["close"]], 5),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA10",
            y_axis=moving_average(stock_data_extracted[["close"]], 10),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA30",
            y_axis=moving_average(stock_data_extracted[["close"]], 30),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA60",
            y_axis=moving_average(stock_data_extracted[["close"]], 60),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA120",
            y_axis=moving_average(stock_data_extracted[["close"]], 120),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA240",
            y_axis=moving_average(stock_data_extracted[["close"]], 240),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="MA360",
            y_axis=moving_average(stock_data_extracted[["close"]], 360),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )

    # 将K线图和移动平均线显示在一个图内
    kline.overlap(line)

    # 成交量柱形图
    x = stock_data_extracted[["date"]].values[:, 0].tolist()
    y = stock_data_extracted[["volume"]].values[:, 0].tolist()

    bar = (
        Bar()
            .add_xaxis(x)
            .add_yaxis("volume", y, label_opts=opts.LabelOpts(is_show=False),
                       itemstyle_opts=opts.ItemStyleOpts(color="#008080"))
            .set_global_opts(title_opts=opts.TitleOpts(title="volume", pos_top="70%"),
                             legend_opts=opts.LegendOpts(is_show=False),
                             )
    )

    # 使用网格将多张图标组合到一起显示
    grid_chart = Grid()

    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", height="55%"),
    )

    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top="70%", height="20%"),
    )

    grid_chart.render("kline_test.html")
    wb.open("d:/kline_test.html")



'''----------------------------------------------第四步：单机UI-wxPython------------------------------------------------'''
# test_01 创建一个窗口
def try_wx_F():
    app = wx.App()
    frame = wx.Frame(None, -1, "Hello, World!")
    frame.Show(True)
    app.MainLoop()

# 万能框架填空模板
def My_App_Windows():
    APP_TITLE = u'基本框架'
    APP_ICON = 'res/python.ico'  # 请更换成你的icon

    class mainFrame(wx.Frame):
        '''程序主窗口类，继承自wx.Frame'''

        def __init__(self):
            '''构造函数'''

            wx.Frame.__init__(self, None, -1, APP_TITLE, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
            # 默认style是下列项的组合：wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN

            self.SetBackgroundColour(wx.Colour(224, 224, 224))
            self.SetSize((800, 600))
            self.Center()

            # 以下代码处理图标
            if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
                exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
                icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
            else:
                icon = wx.Icon(APP_ICON, wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

            # 以下可以添加各类控件
            pass

    class mainApp(wx.App):
        def OnInit(self):
            self.SetAppName(APP_TITLE)
            self.Frame = mainFrame()
            self.Frame.Show()
            return True

    if __name__ == "__main__":
        app = mainApp(redirect=True, filename="debug.txt")
        app.MainLoop()



'''---------------------------------------------------*软件打包*------------------------------------------------------'''
# 运用PyInstall打包代码->.exe




"""==================================================='Package'======================================================"""
# Package1
def outside_Br_NYoil_NYgas_show():
    '''
    集成模块
    功能:
        1.将数据从网上获取存为DataFrame
        2.将df格式存为.csv文件
        3.连接数据库
        4.分别将各自的.csv文件数据写入mysql数据库中
    '''

    # 外盘-期货数据获取并存数据库
    # 爬取数据存为.csv
    outside_history_brent_oil_data().to_csv('外盘-布伦特原油历史数据.csv', index=False)
    outside_history_newyork_oil_data().to_csv('外盘-纽约原油历史数据.csv', index=False)
    outside_history_newyork_natural_gas_data().to_csv('外盘-纽约天然气历史数据.csv', index=False)
    print('连接到MySQL服务器...')
    time.sleep(2)  # 初始化，等待2second
    print('...')
    con = create_engine(
        'mysql+pymysql://root:970804@localhost:3306/stock_finance?charset=utf8')  # 'root'代表本地数据库的名称，冒号后面的’number‘代表的是进入数据库的密码，端口号为：3306/数据库的名称？charset代表字符类别
    time.sleep(1)
    print('...'
          '\nMySQL连接成功！')

    # connect_mysql()

    # 将获取的数据表.csv存写入Mysql数据库中（好像可以不要存csv表，直接存入数据库，已证实失败写入）
    outside_history_brent_oil_data().to_sql('brent_oil_history', con=con, index_label=['id'], if_exists='replace',
                                            dtype={'id': types.BigInteger(), 'date': types.DATE, 'open': types.FLOAT,
                                                   'high': types.FLOAT, 'low': types.FLOAT, 'close': types.FLOAT,
                                                   'volume': types.INT})

    # con.close()   # pandas的to_sql

    # 将获取的纽约原油数据.csv写入MySQL中
    outside_history_newyork_oil_data().to_sql('newyork_oil_history', con=con, index_label=['id'], if_exists='replace',
                                              dtype={'id': types.BigInteger(), 'date': types.DATE, 'open': types.FLOAT,
                                                     'high': types.FLOAT, 'low': types.FLOAT, 'close': types.FLOAT,
                                                     'volume': types.INT})

    # 将获取的纽约天然气数据.csv写入MySQL中
    outside_history_newyork_natural_gas_data().to_sql('newyork_gas_history', con=con, index_label=['id'],
                                                      if_exists='replace',
                                                      dtype={'id': types.BigInteger(), 'date': types.DATE,
                                                             'open': types.FLOAT,
                                                             'high': types.FLOAT, 'low': types.FLOAT,
                                                             'close': types.FLOAT,
                                                             'volume': types.INT})

    print('数据库已关闭！')

    # 可视化基础（有待进一步的2.0版本进阶）
    # outside_history_brent_oil_data().plot()
    # outside_history_newyork_oil_data().plot()
    # outside_history_newyork_natural_gas_data().plot()
    # plt.show()

#Packge2



""" ---------------------------------------------------> main. <---------------------------------------------------- """
def main_f():

    # 数据库操作
    connect_mysql()

    # 汇率计算
    # Exchange_Rate_Realtime_By_self(url_choose="http://webforex.hermes.hexun.com/forex/quotelist?code=FOREXUSDCNY&column=Code,Price", currency_name='美元')
    # Exchange_Rate_Realtime_By_self(url_choose="http://webforex.hermes.hexun.com/forex/quotelist?code=FOREXGBPCNY&column=Code,Price", currency_name='英镑')

    # 外盘-期货汇总
    # outside_Br_NYoil_NYgas_show()
    # get_data()

    #汇率兑换
    # RMB_Covert_GBP()
    # RMB_Covert_USD()

    # 爬虫->存数据->可视化
    # show_kline()

    try_wx_F()








pd.set_option('display.max_columns',None)   # 强制显示所有列



main_f()


'''----------project requirement----------'''
'''---------------期货数据获取--------------'''
# inside_realtime_data()                                # slow & troubles
# outside_history_data()                                 # successful grab  repetition
# outside_realtime_data()                                # successful grab  obj
# inside_history_data()                                  # successful grab  obj
# outside_history_brent_oil_data()                       # successful grab  obj
# outside_history_newyork_natural_gas_data()             # successful grab  obj
# outside_history_newyork_oil_data()                     # successful grab  obj

'''---------------A股三大指数获取------------'''
# Realtime_Market_Index()                                # successful grab  obj
# History_Market_Index_xinlang()                         # successful grab  obj
# Sci_Tech_Broad_Realtime_Index()                        # successful grab  obj
# tu_index_basic()                                       # successful grab
# tu_index_daily_situation()                             # 无用

'''-----------------汇率转换----------------'''
# Covert_RMB_Realtime()                                  # successful grab  obj

# Currency_Exchange_Price()                             # troubles
# RMB_Covert_USD()                                      # troubles
# RMB_Covert_GBP()                                      # troubles

# Exchange_Rate_Realtime_By_self()                       # successful grab  obj

# Currency_New_Price()
# Currency_History_Price()

'''------------extend content-------------'''
# realtime_data()                                        # successful grab
# global_commodity_futures()                             # successful grab
# SH_stock_situation()                                   # successful grab
# SZ_stock_situation()                                   # successful grab
# SH_market_daily_situation()                            # successful grab
# Realtime_market_situation()                            # successful grab
# History_market_situation()                             # successful grab

# Js_world_realtime_news()                               # successful grab
# one_stock_news()                                       # successful grab
# argus_world_watch()                                   # troubles





