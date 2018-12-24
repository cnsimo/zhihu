#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : cnsimo
# @Link    : http://scriptboy.cn


from login_config import *
import requests
from requests.utils import dict_from_cookiejar
import time
import json
from http import cookiejar
import re
import hmac
import hashlib
from urllib.parse import urlencode


class ZhihuAccount(object):
    """
    模拟知乎登录
    """
    def __init__(self):
        self.login_url = LOGIN_URL
        self.captcha_api = CAPTCHA_API
        self.auth_api = AUTH_API
        self.login_data = FORM_DATA.copy()
        self.session = requests.session()
        self.session.headers = HEADERS.copy()
        self.session.cookies = cookiejar.LWPCookieJar(filename='../cookies.txt')

        self.session.get(self.login_url)

    def _get_xsrf(self):
        '''
        拿到token
        :return: X-Xsrftoken
        '''
        cookies = dict_from_cookiejar(self.session.cookies)
        # token = re.findall(r'_xsrf=(.*?);', res.headers.get('Set-Cookie'))
        return cookies['_xsrf']

    # def _get_x_udid(self):
    #     '''
    #     拿到X-UDID
    #     :return:
    #     '''
    #     cookies = dict_from_cookiejar(self.session.cookies)
    #     print(cookies)
    #     print(re.findall(r'(.*?)\|', cookies['d_c0'])[0].strip('"'))
    #     return re.findall(r'(.*?)\|', cookies['d_c0'])[0].strip('"')

    def _get_captcha(self, headers, etag=None):
        '''
        验证码识别,刷新后验证码消失
        :return:
        '''
        headers = headers.copy()
        if etag:
            headers.update({
                'If-None-Match': etag
            })
        res = self.session.get(self.captcha_api+self.login_data.get('lang', 'en'), headers=headers)
        print('X-Req-ID 1: ', res.headers.get('X-Req-ID'))
        show_captcha = re.search(r'true', res.text)
        print('出现验证码，带Etag参数重新请求' if show_captcha else '无验证码')
        if show_captcha:
            self.session.get(self.login_url)
            self._get_captcha(headers, etag=res.headers.get('etag'))
        return ''

    def _get_signature(self, timestamp):
        '''
        知乎signature的生成算法
        :param timestamp: 时间戳
        :return:
        '''
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data.get('grant_type', 'password')
        client_id = self.login_data.get('client_id')
        source = self.login_data.get('source', 'com.zhihu.web')
        ha.update((grant_type+client_id+source+timestamp).encode('utf-8'))
        return ha.hexdigest()

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        resp = self.session.get(self.login_url, allow_redirects=False)
        if not resp.status_code == 200:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            return True
        return False

    def login(self, username=None, password=None):
        '''
        知乎账户模拟登录
        :return:
        '''
        headers = self.session.headers.copy()
        headers.update({
            'authorization': 'oauth '+self.login_data.get('client_id'),
            'X-Xsrftoken': self._get_xsrf(),
            # 'X-UDID': self._get_x_udid()
        })
        timestamp = str(int(time.time()*1000))
        captcha = self._get_captcha(headers)
        signature = self._get_signature(timestamp)
        self.login_data.update({
            'timestamp': timestamp,
            'signature': signature,
            'captcha': captcha
        })
        res = self.session.post(self.auth_api, data=self.login_data, headers=headers)
        print('X-Req-ID 2: ', res.headers.get('X-Req-ID'))
        res = json.loads(res.text)
        print(res)
        if 'error' in res:
            print('登录失败，原因: ' + res['error']['message'])
            return False
        if self.check_login():
            print('登录成功！')
            return True
        print('登录失败！')
        return False


if __name__ == '__main__':
    account = ZhihuAccount()
    account.login()
