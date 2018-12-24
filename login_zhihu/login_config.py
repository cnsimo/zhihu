#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : cnsimo
# @Link    : http://scriptboy.cn

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/65.0.3325.181 Safari/537.36',
    'Host': 'www.zhihu.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.zhihu.com/signin'
}
AUTH_API = 'https://www.zhihu.com/api/v3/oauth/sign_in'
CAPTCHA_API = 'https://www.zhihu.com/api/v3/oauth/captcha?lang='
LOGIN_URL = 'https://www.zhihu.com/signin'
FORM_DATA = {
    'username': '+8615732168817',
    'password': '157lllnnnQ123',
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'ref_source': 'other_',
    'lang': 'en'
}

