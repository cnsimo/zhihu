#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-14 17:34:47
# @Author  : cnsimo
# @Link    : http://scriptboy.cn
# @Version : $Id$


class Topic:
    """
    话题类
    """

    def __init__(self, tid, name=None, followers=None, description=None, parent=None, son=None):
        self._id = tid
        self._name = '' if not isinstance(name, str) else name
        self._followers = 0 if not isinstance(followers, int) else followers
        self._description = '' if not isinstance(description, str) else description
        parent = list(filter(lambda x: isinstance(x, int), parent))
        self._parent = [-1] if not parent else parent
        son = list(filter(lambda x: isinstance(x, int), son))
        self._son = [] if not son else son

    def setname(self, name):
        """
        设置话题名称
        :param name:话题名称
        :return:
        """
        if isinstance(name, str):
            self._name = name
        else:
            raise ValueError('话题名称应该为一个string！')

    def getname(self):
        """
        获得话题名称
        :return: str
        """
        return self._name

    def setdescription(self, description):
        """
        设置话题描述
        :param description:话题描述
        :return:
        """
        if isinstance(description, str):
            self._description = description
        else:
            raise ValueError('话题描述应该为一个string！')

    def getdescription(self):
        """
        获得话题描述
        :return: str
        """
        return self._description

    def setfollowers(self, followers):
        """
        设置话题关注人数
        :param followers: 话题关注人数
        :return:
        """
        if isinstance(followers, int):
            self._followers = followers
        else:
            raise ValueError('关注人数应该为一个Integer！')

    def getfollowers(self):
        """
        获得话题关注人数
        :return: Integer
        """
        return self._followers

    def gettopicid(self):
        """
        获得话题ID
        :return: Integer
        """
        return self._id

    def addparenttopic(self, tid):
        """
        添加父话题
        :param tid: Integer or list of Integer，话题ID
        :return:
        """
        if isinstance(tid, int):
            self._parent.append(tid)
        if isinstance(tid, list):
            for i in tid:
                if not isinstance(i, int):
                    raise ValueError('ID值应该为Integer或整型list！')
            self._parent += tid
        else:
            raise ValueError('ID值应该为Integer或整型list！')

    def getsubtopic(self):
        """
        返回子话题列表
        """
        return self._son

    def addsubtopic(self, tid):
        """
        添加子话题
        :param tid: Integer or list of Integer, 话题ID
        :return:
        """
        if isinstance(tid, int):
            self._son.append(tid)
        if isinstance(tid, list):
            for i in tid:
                if not isinstance(i, int):
                    raise ValueError('ID值应该为Integer或整型list！')
            self._son += tid
        else:
            raise ValueError('ID值应该为Integer或整型list！')

    def todict(self):
        """
        生成字典
        :return: dict
        """
        topic_info = {'id': self._id,
                      'name': self._name,
                      'description': self._description,
                      'followers': self._followers,
                      'parent': self._parent,
                      'son': self._son}
        return topic_info

    def __str__(self):
        info = '''----------------------------
id: {tid}
name: {name}
description: {description}
followers: {followers}
parent: {parent}
son: {son}
----------------------------'''.format(tid=self._id,
                                       name=self._name,
                                       description=self._description[:30],
                                       followers=self._followers,
                                       parent=','.join(map(str, self._parent)),
                                       son=','.join(map(str, self._son)) if self._son else 'Empty')
        return info

    __repr__ = __str__


if __name__ == '__main__':
    t = Topic(123454, name='跟话题', followers=122, description='这个话题已经被锁定！', parent=['123', 'fasdf'], son=['123', 454643])
    print(t)
