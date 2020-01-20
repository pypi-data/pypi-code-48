# -*- coding: utf-8 -*-
# this file is generated by gen_quote_domain function, dont't change it
from sqlalchemy.ext.declarative import declarative_base

from zvdata.contract import register_schema
from zvt.domain.quotes import BlockKdataCommon

KdataBase = declarative_base()


class Block1wkKdata(KdataBase, BlockKdataCommon):
    __tablename__ = 'block_1wk_kdata'


register_schema(providers=['eastmoney'], db_name='block_1wk_kdata', schema_base=KdataBase)

__all__ = ['Block1wkKdata']
