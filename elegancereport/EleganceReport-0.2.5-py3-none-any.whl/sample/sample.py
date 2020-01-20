"""
@Version: 1.0
@Project: EleganceReport
@Author: Raymond
@Data: 2019/12/19午3:48
@File: sample.py
"""
import unittest
from EleganceReport import EleganceReport

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.discover('../tests', pattern='test*.py')
    result = EleganceReport(test_suite)
    result.report(filename='测试报告', description='测试deafult报告', log_path='.')
