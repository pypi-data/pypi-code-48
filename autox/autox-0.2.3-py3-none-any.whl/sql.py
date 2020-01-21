#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 通用包：常用SQL

import importlib
import sys

importlib.reload(sys)


getCaseInfo = "select case_info from t_case where id in (select case_id from t_matching where set_id in " \
           "(select id from t_set where set_name like '%s'))"

getSetName = "select set_name from t_set where set_name like '%s'"


insertSet = "insert into t_set (set_name) values ('%s')"

updateSet = "update t_set set set_name = '%s' where id = '%d'"

deleteSet = "delete from t_set where id = '%d'"

