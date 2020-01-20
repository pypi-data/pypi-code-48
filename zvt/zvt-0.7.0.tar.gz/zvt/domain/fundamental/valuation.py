# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

from zvdata import Mixin
from zvdata.contract import register_schema

ValuationBase = declarative_base()


class StockValuation(ValuationBase, Mixin):
    __tablename__ = 'stock_valuation'

    code = Column(String(length=32))
    name = Column(String(length=32))
    # 总股本(股)
    capitalization = Column(Float)
    # 公司已发行的普通股股份总数(包含A股，B股和H股的总股本)
    circulating_cap = Column(Float)
    # 市值
    market_cap = Column(Float)
    # 流通市值
    circulating_market_cap = Column(Float)
    # 换手率
    turnover_ratio = Column(Float)
    # 静态pe
    pe = Column(Float)
    # 动态pe
    pe_ttm = Column(Float)
    # 市净率
    pb = Column(Float)
    # 市销率
    ps = Column(Float)
    # 市现率
    pcf = Column(Float)


class EtfValuation(ValuationBase, Mixin):
    __tablename__ = 'etf_valuation'

    code = Column(String(length=32))
    name = Column(String(length=32))
    # 静态pe
    pe = Column(Float)
    # 动态pe
    pe_ttm = Column(Float)
    # 市净率
    pb = Column(Float)
    # 市销率
    ps = Column(Float)
    # 市现率
    pcf = Column(Float)


register_schema(providers=['joinquant'], db_name='valuation', schema_base=ValuationBase)

__all__ = ['StockValuation', 'EtfValuation']
