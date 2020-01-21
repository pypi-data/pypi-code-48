__author__ = 'v.denisov'

import allure
from ptst_swagger.config_host import ConfigHost as config
from ptst_swagger.reguest import RegustsHelper as rh

class SwaggerClient():

    def __init__(self):
        pass

    @classmethod
    @allure.step('get paths_sw')
    def get_paths_sw(self):
        return config.paths_sw

    @classmethod
    @allure.step('set url_host')
    def set_url_host(self, value):
        config.url_host = value

    @classmethod
    @allure.step('get url_host')
    def get_url_host(self):
        return config.url_host

    @classmethod
    @allure.step('get')
    def get(self, paths=''):
        url = config.url_host + paths
        cookies = config.cookies
        response = rh.get(url=url, cookies=cookies)
        return response

    @classmethod
    @allure.step('post')
    def post(self, paths='', data=None, params=None, headers=None):
        url = config.url_host + paths
        cookies = config.cookies
        print('cookies=', cookies)
        response = rh.post(url=url, cookies=cookies, data=data, params=params, headers=headers)
        return response


