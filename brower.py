# -*- coding: utf-8 -*-
# @time: 2019-05-13 17:34
# @Author  : zpy
# @Email   : zpy94254@gmail.com
# @file: brower.py

import requests
from logging import getLogger
from utils import BrowerInfo
import time
from twisted.internet.error import (
    TimeoutError, TCPTimedOutError)

log = getLogger('fakebrower')

def get_proxy(proxy_type):
    return requests.get(f'127.0.0.1:5000/getproxy?proxytype={proxy_type}')


class FakeBrower(object):

    def __init__(self, settings):
        self.use_proxy = settings.get("USE_PROXY", True) # 是否启用代理，默认开启
        self.brower_info = BrowerInfo(url=settings.get('BROWERINFO_URL'))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        self.req_start = time.time()
        proxy_type = request.url.split(':')[0]
        if 'proxy' in request.meta:
            if 'exception' in request.meta and not request.meta["exception"]:
                return
            request.meta['proxy'] = self.brower_info.get_proxy(proxy_type, spider.name) # 替换
        if self.use_proxy:
            request.meta['proxy'] = self.brower_info.get_proxy(proxy_type, spider.name) # 初始化获取
            request.headers['User-Agent'] = self.brower_info.get_ua()

    def process_response(self, request, response, spider):
        self.brower_info.put_proxy(request.meta['proxy'],
                                   spider.name,
                                   1)
        log.info(f"proxy={request.meta['proxy']} cost={time.time()-self.req_start}")
        return response

    def process_exception(self, request, exception, spider):
        if 'proxy' not in request.meta:
            return
        if exception:
            request.meta['exception'] = True
            if isinstance(exception, (TimeoutError, TCPTimedOutError)):
                self.brower_info.del_proxy(request.meta['proxy'], spider.name)
            else:
                self.brower_info.put_proxy(request.meta['proxy'],
                                           spider.name,
                                           -1)