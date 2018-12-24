#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-14 17:34:47
# @Author  : cnsimo
# @Link    : http://scriptboy.cn
# @Version : $Id$

from config import *
from topic import Topic
import time
import requests
from bs4 import BeautifulSoup
import pymysql


connection = None


def getsession():
    """
    得到一个requests会话
    :return: session
    """
    session = requests.session()
    session.headers.update(HEADERS)
    session.cookies = requests.utils.cookiejar_from_dict(cookiesfromstr(COOKIE))
    return session


def getconnection():
    """
    获取MySql数据库连接，重连3次后无响应将终止程序运行
    :return: conn
    """
    retry = 0
    print('正在创建MySql会话...')

    def connectionmysql():
        nonlocal retry
        try:
            c = pymysql.connect(host=MYSQL_HOST,
                                user=MYSQL_USER,
                                password=MYSQL_PASS,
                                db=MYSQL_DB,
                                charset=MYSQL_CHARSET,
                                cursorclass=pymysql.cursors.DictCursor)
            return c
        except pymysql.err.OperationalError:
            retry += 1
            return None

    conn = connectionmysql()
    while retry <= 3:
        if conn:
            print('创建MySql会话成功!')
            return conn
        else:
            print('正在尝试第%d次...' % (retry))
            conn = connectionmysql()
    else:
        print('MySql服务连接异常，请稍后再试！')
        print('程序终止运行！')
        exit()


def gethtml(topic_id):
    """
    得到某话题页的源码
    :param topic_id:
    :return: res.text
    """
    res = s.get(URL_PATTERN % topic_id, allow_redirects=False)
    if res.status_code == 200:
        return res.text
    else:
        return None


def cookiesfromstr(c):
    """
    转换字符串的cookies值到字典类型
    :param c:
    :return: c_dict
    """
    c_dict = {}
    c_list = c.split(';')
    for item in c_list:
        key, value = item.strip().split('=', 1)
        c_dict[key.strip()] = value.strip()
    return c_dict


def getanstopic(html):
    """
    从源码中获得父话题。
    :param html: 待解析的HTML源码
    :return: anstopic_list
    """
    ans_list = []
    soup = BeautifulSoup(html, 'lxml')
    tagsdiv = soup.find('div', attrs={'id': 'zh-topic-organize-parent-editor'})
    ans_tags = tagsdiv.find_all('a', attrs={'class': 'zm-item-tag'})
    for tag in ans_tags:
        ans_list.append(tag['href'].strip())
    if not ans_list:
        ans_list.append('-1')
    else:
        ans_list = list(map(lambda x: int(x.split('/')[-2]), ans_list))
    return ans_list


def getsubtopic(html):
    """
    从源码中获得子话题
    :param html: 待解析的HTML源码
    :return: subtopic_list
    """
    sub_list = []
    soup = BeautifulSoup(html, 'lxml')
    tagsdiv = soup.find('div', attrs={'id': 'zh-topic-organize-child-editor'})
    ans_tags = tagsdiv.find_all('a', attrs={'class': 'zm-item-tag'})
    for tag in ans_tags:
        sub_list.append(tag['href'].strip())

    if sub_list:
        sub_list = list(map(lambda x: int(x.split('/')[-2]), sub_list))
    return sub_list


def gettopicinfo(html, tid):
    """
    从源码中获取当前话题信息
    :param html: 待解析的HTML源码
    :return: Topic类实例
    """
    soup = BeautifulSoup(html, 'lxml')
    name = soup.find('h1', attrs={'class': 'zm-editable-content'}).get_text().strip()
    tag_followers = soup.find('div', attrs={'class': 'zm-topic-side-followers-info'}).find('a')
    followers = tag_followers.get_text().strip() if tag_followers else '0'
    description = soup.find('div', attrs={'id': 'zh-topic-desc'}).find('div', attrs={'class': 'zm-editable-content'}).get_text().strip()
    parent = getanstopic(html)
    son = getsubtopic(html)
    return Topic(tid, name=name, followers=int(followers), parent=parent, son=son, description=description)


def savetomysql(t):
    """
    保存话题到数据库。
    :param t: Topic实例
    :return:
    """
    t = t.todict()
    t['parent'] = ','.join(list(map(str, t['parent'])))
    t['son'] = ','.join(list(map(str, t['son'])))
    topic_tuple = (t['id'], t['name'], t['followers'], t['description'], t['parent'], t['son'])
    with connection.cursor() as cursor:
        sql = 'SELECT * FROM t_topic WHERE t_topic_id='+str(t['id'])
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            return None
    with connection.cursor() as cursor:
        sql = 'INSERT INTO t_topic VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, topic_tuple)
    connection.commit()
    print('话题', t['id'], '已保存到MySQL！', t)


def deepcrawl(topic_id):
    """
    递归爬取话题树
    :param topic_id: 正在访问的话题
    :return:
    """
    content = gethtml(topic_id)
    if not content:
        raise ConnectionError('无法正常获取网页内容！')
    t = gettopicinfo(content, int(topic_id))
    savetomysql(t)
    time.sleep(0.05)
    for sub in t.getsubtopic():
        deepcrawl(sub)


def startcrawl():
    """
    启动爬虫
    :return:
    """
    global connection
    connection = getconnection()

    deepcrawl(ROOT_TOPIC_ID)

    connection.close()
    print('爬虫正常终止。')


if __name__ == '__main__':
    s = getsession()
    startcrawl()
    s.close()
