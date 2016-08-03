#!/usr/bin/env python
#coding:utf8
import threading,time,pymongo
from pymongo import MongoClient
from Queue import Queue
#消息入队
class MsgInQueue():
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data=queue
    def putmsgqueue(self,msg):
        self.data.put(msg)
        print 'put msg in queue success:'+msg['Content']

#消息出队并存入数据库
class MsgOutQueue2db(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data = queue
        #建立MongoDB连接
        self.conn = MongoClient()
        #数据库
        self.db = self.conn.wechatRobot
        #数据表
        self.messages = self.db.messages
    def run(self):
        while 1:
            try:
                # print self.data
                #从队列里取消息
                msg = self.data.get(1, 5)  # get(self, block=True, timeout=None) ,1就是阻塞等待,5是超时5秒
                print "%s: %s get %s from queue !" % (time.ctime(), self.getName(), msg['Content'].encode('utf-8'))
                try:
                    #格式化消息数据
                    m = dict(groupname=msg['FromUserName'].encode('utf-8'),
                             time=msg['CreateTime'],
                             username=msg['ActualUserName'],
                             usernickname=msg['ActualNickName'].encode('utf-8'),
                             message=msg['Content'].encode('utf-8'),
                             messagetype=msg['MsgType']
                             )
                    print m
                    #存入数据库
                    self.db.messages.insert(m)
                    time.sleep(1)
                except  Exception, e:
                    print e
                    continue
            except  Exception, e:
                continue
