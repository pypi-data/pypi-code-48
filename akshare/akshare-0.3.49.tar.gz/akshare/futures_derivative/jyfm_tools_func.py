# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Author: Albert King
date: 2020/01/02 17:37
contact: jindaxiang@163.com
desc: 获取交易法门-工具: https://www.jiaoyifamen.com/tools/
交易法门首页: https://www.jiaoyifamen.com/
# 增加-交易法门-工具-期限分析-
增加-交易法门-工具-期限分析-基差日报
增加-交易法门-工具-期限分析-基差分析
增加-交易法门-工具-期限分析-期限结构
增加-交易法门-工具-期限分析-价格季节性

# 交易法门-工具-仓单分析
交易法门-工具-仓单分析-仓单日报
交易法门-工具-仓单分析-仓单查询
交易法门-工具-仓单分析-虚实盘比查询

# 交易法门-工具-资讯汇总
交易法门-工具-资讯汇总-研报查询
交易法门-工具-资讯汇总-交易日历

# 交易法门-工具-资金分析
交易法门-工具-资金分析-资金流向
"""
import requests
import pandas as pd
import matplotlib.pyplot as plt

from akshare.futures_derivative.jyfm_login_func import jyfm_login

from akshare.futures_derivative.cons import (
    csa_payload,
    csa_url_spread,
    csa_url_ratio,
    csa_url_customize,
)


# 交易法门-工具-套利分析
def jyfm_tools_futures_spread(
        type_1="RB", type_2="RB", code_1="01", code_2="05", headers="", plot=True
):
    """
    交易法门-工具-套利分析-跨期价差(自由价差)
    :param type_1: str
    :param type_2: str
    :param code_1: str
    :param code_2: str
    :param plot: Bool
    :return: pandas.Series or pic
    """
    csa_payload_his = csa_payload.copy()
    csa_payload_his.update({"type1": type_1})
    csa_payload_his.update({"type2": type_2})
    csa_payload_his.update({"code1": code_1})
    csa_payload_his.update({"code2": code_2})
    res = requests.get(csa_url_spread, params=csa_payload_his, headers=headers)
    data_json = res.json()
    data_df = pd.DataFrame([data_json["category"], data_json["value"]]).T
    data_df.index = pd.to_datetime(data_df.iloc[:, 0])
    data_df = data_df.iloc[:, 1]
    data_df.name = "value"
    if plot:
        data_df.plot()
        plt.legend(loc="best")
        plt.xlabel("date")
        plt.ylabel("value")
        plt.show()
        return data_df
    else:
        return data_df


def jyfm_tools_futures_ratio(
        type_1="RB", type_2="RB", code_1="01", code_2="05", headers="", plot=True
):
    """
    交易法门-工具-套利分析-自由价比
    :param type_1: str
    :param type_2: str
    :param code_1: str
    :param code_2: str
    :param plot: Bool
    :return: pandas.Series or pic
    2013-01-04   -121
    2013-01-07   -124
    2013-01-08   -150
    2013-01-09   -143
    2013-01-10   -195
                 ...
    2019-10-21    116
    2019-10-22    126
    2019-10-23    123
    2019-10-24    126
    2019-10-25    134
    """
    csa_payload_his = csa_payload.copy()
    csa_payload_his.update({"type1": type_1})
    csa_payload_his.update({"type2": type_2})
    csa_payload_his.update({"code1": code_1})
    csa_payload_his.update({"code2": code_2})
    res = requests.get(csa_url_ratio, params=csa_payload_his, headers=headers)
    data_json = res.json()
    data_df = pd.DataFrame([data_json["category"], data_json["value"]]).T
    data_df.index = pd.to_datetime(data_df.iloc[:, 0])
    data_df = data_df.iloc[:, 1]
    data_df.name = "value"
    if plot:
        data_df.plot()
        plt.legend(loc="best")
        plt.xlabel("date")
        plt.ylabel("value")
        plt.show()
        return data_df
    else:
        return data_df


def jyfm_tools_futures_customize(
        formula="RB01-1.6*I01-0.5*J01-1200", headers="", plot=True
):
    """
    交易法门-工具-套利分析-多腿组合
    :param formula: str
    :param plot: Bool
    :return: pandas.Series or pic
    2013-01-04   -121
    2013-01-07   -124
    2013-01-08   -150
    2013-01-09   -143
    2013-01-10   -195
                 ...
    2019-10-21    116
    2019-10-22    126
    2019-10-23    123
    2019-10-24    126
    2019-10-25    134
    """
    params = {"formula": formula}
    res = requests.get(csa_url_customize, params=params, headers=headers)
    data_json = res.json()
    data_df = pd.DataFrame([data_json["category"], data_json["value"]]).T
    data_df.index = pd.to_datetime(data_df.iloc[:, 0])
    data_df = data_df.iloc[:, 1]
    data_df.name = "value"
    if plot:
        data_df.plot()
        plt.legend(loc="best")
        plt.xlabel("date")
        plt.ylabel("value")
        plt.show()
        return data_df
    else:
        return data_df


jyfm_exchange_symbol_dict = {
    "中国金融期货交易所": {
        "TF": "五债",
        "T": "十债",
        "IC": "中证500",
        "IF": "沪深300",
        "IH": "上证50",
        "TS": "二债",
    },
    "郑州商品交易所": {
        "FG": "玻璃",
        "RS": "菜籽",
        "CF": "棉花",
        "LR": "晚稻",
        "CJ": "红枣",
        "JR": "粳稻",
        "ZC": "动力煤",
        "TA": "PTA",
        "SA": "纯碱",
        "AP": "苹果",
        "WH": "强麦",
        "SF": "硅铁",
        "MA": "甲醇",
        "CY": "棉纱",
        "RI": "早稻",
        "OI": "菜油",
        "SM": "硅锰",
        "RM": "菜粕",
        "UR": "尿素",
        "PM": "普麦",
        "SR": "白糖",
    },
    "大连商品交易所": {
        "PP": "PP",
        "RR": "粳米",
        "BB": "纤板",
        "A": "豆一",
        "EG": "乙二醇",
        "B": "豆二",
        "C": "玉米",
        "JM": "焦煤",
        "I": "铁矿",
        "J": "焦炭",
        "L": "塑料",
        "M": "豆粕",
        "P": "棕榈",
        "CS": "淀粉",
        "V": "PVC",
        "Y": "豆油",
        "JD": "鸡蛋",
        "FB": "胶板",
        "EB": "苯乙烯",
    },
    "上海期货交易所": {
        "SS": "不锈钢",
        "RU": "橡胶",
        "AG": "沪银",
        "AL": "沪铝",
        "FU": "燃油",
        "RB": "螺纹",
        "CU": "沪铜",
        "PB": "沪铅",
        "BU": "沥青",
        "AU": "沪金",
        "ZN": "沪锌",
        "SN": "沪锡",
        "HC": "热卷",
        "NI": "沪镍",
        "WR": "线材",
        "SP": "纸浆",
    },
    "上海国际能源交易中心": {"SC": "原油", "NR": "20号胶"},
}


# 交易法门-工具-资讯汇总
def jyfm_tools_research_query(limit="100", headers=""):
    """
    交易法门-工具-资讯汇总-研报查询
    https://www.jiaoyifamen.com/tools/research/qryPageList
    :param limit: 返回条数
    :type limit: str
    :return: 返回研报信息数据
    :rtype: pandas.DataFrame
    """
    url = "https://www.jiaoyifamen.com/tools/research/qryPageList"
    params = {
        "page": "1",
        "limit": limit,
    }
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["data"])


def jyfm_tools_trade_calendar(trade_date="2020-01-03", headers=""):
    """
    交易法门-工具-资讯汇总-交易日历
    此函数可以返回未来的交易日历数据
    https://www.jiaoyifamen.com/tools/trade-calendar/events
    :param trade_date: 指定交易日
    :type trade_date: str
    :return: 返回指定交易日的交易日历数据
    :rtype: pandas.DataFrame
    """
    url = "https://www.jiaoyifamen.com/tools/trade-calendar/events"
    params = {
        "page": "1",
        "limit": "1000",
        "day": trade_date,
    }
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["data"])


# 交易法门-工具-持仓分析
def jyfm_tools_position_detail(
        symbol="JM", code="jm2005", trade_date="2020-01-03", headers=""
):
    """
    交易法门-工具-持仓分析-期货持仓
    :param symbol: 指定品种
    :type symbol: str
    :param code: 指定合约
    :type code: str
    :param trade_date: 指定交易日
    :type trade_date: str
    :param headers: headers with cookies
    :type headers:dict
    :return: 指定品种的指定合约的指定交易日的期货持仓数据
    :rtype: pandas.DataFrame
    """
    url = f"https://www.jiaoyifamen.com/tools/position/details/{symbol}?code={code}&day={trade_date}&_=1578040551329"
    res = requests.get(url, headers=headers)
    return pd.DataFrame(res.json()["short_rank_table"])


def jyfm_tools_position_seat(seat="永安期货", trade_date="2020-01-03", headers=""):
    """
    交易法门-工具-持仓分析-持仓分析-席位持仓
    :param seat: 指定期货公司
    :type seat: str
    :param trade_date: 具体交易日
    :type trade_date: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定期货公司指定交易日的席位持仓数据
    :rtype: pandas.DataFrame
    """
    url = "https://www.jiaoyifamen.com/tools/position/seat"
    params = {
        "seat": seat,
        "day": trade_date,
        "type": "",
        "_": "1578040989932",
    }
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["data"])


# 交易法门-工具-资金分析
def jyfm_tools_position_fund(trade_date="2020-01-08", indicator="沉淀资金排名", headers=""):
    """
    交易法门-工具-资金分析-资金流向
    https://www.jiaoyifamen.com/tools/position/fund/?day=2020-01-08
    :param trade_date: 指定交易日
    :type trade_date: str
    :param indicator: "沉淀资金排名" or "资金流向排名"
    :type indicator: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定交易日的资金流向数据
    :rtype: pandas.DataFrame
    """
    params = {
        "day": trade_date,
    }
    url = "https://www.jiaoyifamen.com/tools/position/fund/"
    res = requests.get(url, params=params, headers=headers)
    data_json = res.json()
    if indicator == "沉淀资金排名":
        return pd.DataFrame([[data_json["tradingDay"]] * len(data_json["category1"]), data_json["category1"], data_json["value1"]], index=["date", "symbol", "fund"]).T
    else:
        return pd.DataFrame([[data_json["tradingDay"]] * len(data_json["category2"]), data_json["category2"], data_json["value2"]], index=["date", "symbol", "fund"]).T


# 交易法门-工具-仓单分析
# TODO 修改输出数据的字段名
def jyfm_tools_warehouse_receipt_daily(trade_date="2020-01-02", headers=""):
    """
    交易法门-工具-仓单分析-仓单日报
    https://www.jiaoyifamen.com/tools/warehouse-receipt/daily
    :param trade_date: 指定交易日
    :type trade_date: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定交易日的仓单日报数据
    :rtype: pandas.DataFrame
    """
    params = {
        "day": trade_date,
        "_": "1578555328412",
    }
    url = "https://www.jiaoyifamen.com/tools/warehouse-receipt/daily"
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["data"])


def jyfm_tools_warehouse_receipt_query(symbol="AL", indicator="仓单数据走势图", headers=""):
    """
    交易法门-工具-仓单分析-仓单查询
    https://www.jiaoyifamen.com/tools/warehouse-receipt/query
    :param symbol: 指定品种
    :type symbol: str
    :param indicator: 指定需要获取的指标, ["仓单数据走势图", "仓单数据季节图"]
    :type indicator: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种的仓单数量走势图/季节图数据
    :rtype: pandas.DataFrame
    """
    params = {
        "type": symbol,
    }
    url = "https://www.jiaoyifamen.com/tools/warehouse-receipt/query"
    res = requests.get(url, params=params, headers=headers)
    data_json = res.json()
    if indicator == "仓单数据走势图":
        return pd.DataFrame([data_json["category"], data_json["value"], data_json["value2"]]).T
    return pd.DataFrame([data_json["dataCategory"], data_json["year2013"], data_json["year2014"], data_json["year2015"],
                         data_json["year2016"], data_json["year2017"], data_json["year2018"], data_json["year2019"],
                         data_json["year2020"]],
                        index=["date", "year2013", "year2014", "year2015", "year2016", "year2017", "year2018",
                               "year2019", "year2020"]).T


def jyfm_tools_warehouse_virtual_fact_daily(trade_date="2020-01-20", headers=""):
    """
    交易法门-工具-仓单分析-虚实盘比日报
    https://www.jiaoyifamen.com/tools/warehouse-receipt/virtualfact/daily?day=&_=1579532255369
    :param trade_date: 指定日期
    :type trade_date: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种指定合约的虚实盘比数据
    :rtype: pandas.DataFrame
    """
    params = {
        "day": trade_date,
        "_": "1579532255370",
    }
    url = "https://www.jiaoyifamen.com/tools/warehouse-receipt/virtualfact/daily"
    res = requests.get(url, params=params, headers=headers)
    data_json = res.json()["data"]
    return pd.DataFrame(data_json)


def jyfm_tools_warehouse_virtual_fact_ratio(symbol="AL", code="05", headers=""):
    """
    交易法门-工具-仓单分析-虚实盘比查询
    https://www.jiaoyifamen.com/tools/warehouse-receipt/ratio
    :param symbol: 指定品种
    :type symbol: str
    :param code: 指定日期的合约
    :type code: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种指定合约的虚实盘比数据
    :rtype: pandas.DataFrame
    """
    params = {
        "type": symbol,
        "code": code,
    }
    url = "https://www.jiaoyifamen.com/tools/warehouse-receipt/ratio"
    res = requests.get(url, params=params, headers=headers)
    data_json = res.json()
    return pd.DataFrame([data_json["dataCategory"], data_json["year2013"], data_json["year2014"], data_json["year2015"],
                         data_json["year2016"], data_json["year2017"], data_json["year2018"], data_json["year2019"],
                         data_json["year2020"]],
                        index=["date", "year2013", "year2014", "year2015", "year2016", "year2017", "year2018",
                               "year2019", "year2020"]).T


# 交易法门-工具-期限分析
def jyfm_tools_futures_basis_daily(trade_date="2020-01-02", headers=""):
    """
    交易法门-工具-期限分析-基差日报
    :param trade_date: 指定交易日期, 注意格式为 "2020-01-02"
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定日期的基差日报数据
    :rtype: pandas.DataFrame
    """
    params = {
        "day": trade_date,
    }
    url = "https://www.jiaoyifamen.com/tools/future/basis/daily"
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["table_data"])


def jyfm_tools_futures_basis_analysis_area(symbol="Y", headers=""):
    """
    交易法门-工具-期限分析-基差日报-地区选取
    :param symbol: 品种代码
    :type symbol: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种的可选地区
    :rtype: list
    """
    params = {
        "type": symbol,
    }
    url = "https://www.jiaoyifamen.com/tools/future/area"
    res = requests.get(url, params=params, headers=headers)
    return res.json()["areas"]


def jyfm_tools_futures_basis_analysis(symbol="RB", area="上海", headers=""):
    """
    交易法门-工具-期限分析-基差日报
    :param symbol: 品种代码
    :type symbol: str
    :param area: one of ["上海", "天津"], 不同品种不同日期通过 jyfm_tools_futures_basis_analysis_area 返回
    :type area: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种和地区的基差日报
    :rtype: pandas.DataFrame
    """
    params = {
        "type": symbol,
        "area": area,
    }
    url = f"https://www.jiaoyifamen.com/tools/future/basis/daily"
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json())


def jyfm_tools_futures_basis_structure(symbol="RB", headers=""):
    """
    交易法门-工具-期限分析-期限结构
    :param symbol: 合约品种
    :type symbol: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 指定品种的期限结构数据
    :rtype: pandas.DataFrame
    """
    params = {
        "type": symbol,
    }
    url = "https://www.jiaoyifamen.com/tools/future/basis/structure"
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json())


def jyfm_tools_futures_basis_rule(symbol="RB", code="05", return_data="", headers=""):
    """
    交易法门-工具-期限分析-价格季节性
    :param symbol: 品种
    :type symbol: str
    :param code: 合约具体月份
    :type code: str
    :param return_data: 期货涨跌统计 or 季节性走势图, 默认为 季节性走势图
    :type return_data: str
    :param headers: headers with cookies
    :type headers: dict
    :return: 期货涨跌统计 or 季节性走势图
    :rtype: pandas.DataFrame
    """
    params = {
        "type": symbol,
        "code": code,
    }
    url = "https://www.jiaoyifamen.com/tools/future/basis/rule"
    res = requests.get(url, params=params, headers=headers)
    data_json = res.json()
    if return_data == "期货涨跌统计":
        return pd.DataFrame(data_json["ratioData"])
    return pd.DataFrame([data_json["dataCategory"], data_json["year2013"], data_json["year2014"], data_json["year2015"],
                         data_json["year2016"], data_json["year2017"], data_json["year2018"], data_json["year2019"],
                         data_json["year2020"]],
                        index=["date", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]).T


# 交易法门-工具-交易规则
def jyfm_tools_receipt_expire_info(headers=""):
    """
    交易法门-工具-交易规则-仓单有效期
    :param headers: headers with cookies
    :type headers: dict
    :return: all history data
    :rtype: pandas.DataFrame
    """
    temp_df = pd.DataFrame()
    for page in range(1, 4):
        params = {
            "page": str(page),
            "limit": "20",
        }
        res = requests.get(
            f"https://www.jiaoyifamen.com/tools/receipt-expire-info/all",
            params=params,
            headers=headers,
        )
        temp_df = temp_df.append(pd.DataFrame(res.json()["data"]), ignore_index=True)
    return temp_df


def jyfm_tools_position_limit_info(exchange="CFFEX", headers=""):
    """
    交易法门-工具-交易规则-限仓规定
    :param exchange: one of ["INE", "DCE", "CZCE", "SHFE", "CFFEX"], default is "CFFEX"]
    :type exchange: str
    :param headers: headers with cookies
    :type headers: dict
    :return:
    :rtype: pandas.DataFrame
    """
    params = {
        "page": "1",
        "limit": "10",
        "exchange": exchange,
    }
    url = "https://www.jiaoyifamen.com/tools/position-limit/query"
    res = requests.get(url, params=params, headers=headers)
    return pd.DataFrame(res.json()["data"])


if __name__ == "__main__":
    # 如果要测试函数, 请先在交易法门网站: https://www.jiaoyifamen.com/ 注册帐号密码, 在下面输入对应的帐号和密码后再运行 jyfm_login 函数!
    headers = jyfm_login(account="link", password="loveloli888")

    # 交易法门-工具-套利分析
    jyfm_tools_futures_spread_df = jyfm_tools_futures_spread(
        type_1="RB", type_2="RB", code_1="01", code_2="05", headers=headers, plot=True
    )
    print(jyfm_tools_futures_spread_df)
    jyfm_tools_futures_ratio_df = jyfm_tools_futures_ratio(
        type_1="RB", type_2="RB", code_1="01", code_2="05", headers=headers, plot=True
    )
    print(jyfm_tools_futures_ratio_df)
    jyfm_tools_futures_customize_df = jyfm_tools_futures_customize(
        formula="RB01-1.6*I01-0.5*J01-1200", headers=headers, plot=True
    )
    print(jyfm_tools_futures_customize_df)

    # 交易法门-工具-资讯汇总
    jyfm_tools_research_query_df = jyfm_tools_research_query(limit="100", headers=headers)
    print(jyfm_tools_research_query_df)
    jyfm_tools_trade_calendar_df = jyfm_tools_trade_calendar(trade_date="2020-01-03", headers=headers)
    print(jyfm_tools_trade_calendar_df)

    # 交易法门-工具-持仓分析
    jyfm_tools_position_detail_df = jyfm_tools_position_detail(
        symbol="JM", code="jm2005", trade_date="2020-01-03", headers=headers
    )
    print(jyfm_tools_position_detail_df)
    jyfm_tools_position_seat_df = jyfm_tools_position_seat(
        seat="永安期货", trade_date="2020-01-03", headers=headers
    )
    print(jyfm_tools_position_seat_df)

    # 交易法门-工具-资金分析
    jyfm_tools_position_fund_df = jyfm_tools_position_fund(trade_date="2020-01-08", indicator="沉淀资金排名", headers=headers)
    print(jyfm_tools_position_fund_df)

    # 交易法门-工具-仓单分析
    # 交易法门-工具-仓单分析-仓单日报
    jyfm_tools_warehouse_receipt_daily_df = jyfm_tools_warehouse_receipt_daily(trade_date="2020-01-02", headers=headers)
    print(jyfm_tools_warehouse_receipt_daily_df)
    # 交易法门-工具-仓单分析-仓单查询
    jyfm_tools_warehouse_receipt_query_df = jyfm_tools_warehouse_receipt_query(symbol="AL", indicator="仓单数据走势图", headers=headers)
    print(jyfm_tools_warehouse_receipt_query_df)
    # 交易法门-工具-仓单分析-虚实盘比日报
    jyfm_tools_warehouse_virtual_fact_daily_df = jyfm_tools_warehouse_virtual_fact_daily(trade_date="2020-01-20", headers=headers)
    print(jyfm_tools_warehouse_virtual_fact_daily_df)
    # 交易法门-工具-仓单分析-虚实盘比查询
    jyfm_tools_warehouse_receipt_ratio_df = jyfm_tools_warehouse_virtual_fact_ratio(symbol="AL", code="05", headers=headers)
    print(jyfm_tools_warehouse_receipt_ratio_df)

    # 交易法门-工具-期限分析
    jyfm_tools_futures_basis_daily_df = jyfm_tools_futures_basis_daily(trade_date="2020-01-02", headers=headers)
    print(jyfm_tools_futures_basis_daily_df)
    jyfm_tools_futures_basis_analysis_area_df = jyfm_tools_futures_basis_analysis_area(symbol="Y", headers=headers)
    print(jyfm_tools_futures_basis_analysis_area_df)
    jyfm_tools_futures_basis_analysis_df = jyfm_tools_futures_basis_analysis(symbol="RB", area="上海", headers=headers)
    print(jyfm_tools_futures_basis_analysis_df)
    jyfm_tools_futures_basis_structure_df = jyfm_tools_futures_basis_structure(symbol="RB", headers=headers)
    print(jyfm_tools_futures_basis_structure_df)
    jyfm_tools_futures_basis_rule_df = jyfm_tools_futures_basis_rule(symbol="RB", code="05", return_data="",
                                                                     headers=headers)
    print(jyfm_tools_futures_basis_rule_df)

    # 交易法门-工具-交易规则
    jyfm_tools_receipt_expire_info_df = jyfm_tools_receipt_expire_info(headers=headers)
    print(jyfm_tools_receipt_expire_info_df)
    jyfm_tools_position_limit_info_df = jyfm_tools_position_limit_info(
        exchange="CFFEX", headers=headers
    )
    print(jyfm_tools_position_limit_info_df)

