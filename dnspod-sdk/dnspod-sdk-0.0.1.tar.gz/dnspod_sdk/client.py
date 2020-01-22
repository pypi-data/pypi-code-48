"""
文档地址
https://www.dnspod.cn/docs/info.html
"""
from urllib.parse import urljoin

import requests


class DnspodClient:
    def __init__(
        self,
        token_id,
        token,
        user_agent,
        format="json",
        lang="cn",
        error_on_empty="yes",
    ):
        """UserAgent的格式必须为：程序英文名称/版本(联系邮箱)，比如：MJJ DDNS Client/1.0.0 (shallwedance@126.com)"""

        self.login_token = f"{token_id},{token}"
        self.format = format
        self.lang = lang
        self.error_on_empty = error_on_empty

        self.headers = {"User-Agent": user_agent}

    def get_req_data(self, data):
        req_data = {
            "login_token": self.login_token,
            "format": self.format,
            "lang": self.lang,
            "error_on_empty": self.error_on_empty,
        }
        req_data.update(data)
        return req_data

    def post(self, path, data={}):
        url = urljoin("https://dnsapi.cn/", path)
        req_data = self.get_req_data(data)
        return requests.post(url, data=req_data, headers=self.headers)
