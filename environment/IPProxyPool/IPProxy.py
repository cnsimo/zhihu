# coding:utf-8

"""
IPProxy
~~~~~~~

这是整个项目的入口函数，运行这个脚本可以使项目正确的运作起来。
"""

from multiprocessing import Value, Queue, Process
from api.apiServer import start_api_server
from db.DataStore import store_data
from validator.Validator import validator, getMyIP
from spider.ProxyCrawl import startProxyCrawl
from config import TASK_QUEUE_SIZE

if __name__ == "__main__":
    """
    通过调用getMyIP()函数获取本机IP，方便代理IP有效性的验证。

    然后分别开启三个线程：p0, p1, p2。
    p0: 启动start_api_server模块，将web服务器启动
    p1: 启动startProxyCrawl模块，开始爬取代理
    p2: 启动validator模块，验证代理IP的有效性
    p3: 启动store_data模块，存储有效代理IP到数据库

    关于进程间的数据共享，这里使用了两种安全的数据共享方式：Queue、Value
    Queue: 这种方式可以存储一个队列，默认block参数值为true，这个时候，put和get操作时若队列为empty或者full的时候会阻塞参数timeout指定的时间，
    超出时间后抛出异常。
    Vlaue: 这种方式与Queue不同的是不会阻塞进程并且保证数据安全，第一个参数取值为'i'/'c'/'b'等等，'i'代表存储int类型数据，第二个参数是具体值。

    DB_PROXY_NUM: 当前已爬取代理的总数。
    q1: 被爬取的所有代理队列。
    q2: 验证可用的代理队列。
    """

    myip = getMyIP()
    DB_PROXY_NUM = Value('i', 0)
    q1 = Queue(maxsize=TASK_QUEUE_SIZE)
    q2 = Queue()
    p0 = Process(target=start_api_server)
    p1 = Process(target=startProxyCrawl, args=(q1, DB_PROXY_NUM,myip))
    p2 = Process(target=validator, args=(q1, q2, myip))
    p3 = Process(target=store_data, args=(q2, DB_PROXY_NUM))
    """当使用join()阻塞进程时，为了不必要的麻烦，这里推荐使用1221的v型排布"""
    p0.start()
    p1.start()
    p2.start()
    p3.start()
    p3.join()
    p2.join()
    p1.join()
    p0.join()
