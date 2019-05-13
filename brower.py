# -*- coding: utf-8 -*-
# @time: 2019-05-13 17:34
# @Author  : zpy
# @Email   : zpy94254@gmail.com
# @file: brower.py

import requests
from logging import getLogger
log = getLogger('fakebrower')

def get_proxy(proxy_type):
    return requests.get(f'127.0.0.1:5000/getproxy?proxytype={proxy_type}')


class FakeBrower(object):

    def __init__(self, settings):
        self.use_proxy = settings.get("USE_PROXY", True) # 是否启用代理，默认开启

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        proxy_type = request.url.split(':')[0]
        if 'proxy' in request.meta:
            if 'exception' in request.meta and not request.meta["exception"]:
                return
            request.meta['proxy'] = get_proxy(proxy_type) # 替换
        if self.use_proxy:
            request.meta['proxy'] = get_proxy(proxy_type) # 初始化获取

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        if exception:
            request.meta['exception'] = True