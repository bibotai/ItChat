#!/usr/bin/env python
#coding:utf8
import threading,time,pymongo
from pymongo import MongoClient
from Queue import Queue
#消息入队
class MsgInQueue():
    def __init__(self, queue):
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
                             messagetype=msg['MsgType'],
                             type=msg['Type']
                             )
                    # print m
                    #存入数据库
                    self.db.messages.insert(m)
                    # 存入统计信息
                    db = Storage2DB()
                    db.GroupMsgStatistics(msg)
                    time.sleep(1)
                except  Exception, e:
                    print e
                    continue
            except  Exception, e:
                continue

class Storage2DB():
   def __init__(self):
        # 建立MongoDB连接
        self.conn = MongoClient()
        # 数据库
        self.db = self.conn.wechatRobot
   def storageGroupName(self,grouplist):
       # 数据表
       self.grouplist = self.db.grouplist
       for item in  grouplist:
           try:
               #查询是否已保存这个群
               one=self.db.grouplist.find_one({'username':item['UserName']})
               if one==None:
                   # 格式化群数据
                   g = dict(username=item['UserName'],
                            grouppy=item['PYQuanPin'],
                            groupname=item['NickName'].encode('utf-8'),
                            time=time.time()
                            )
                   print g
                   # 存入数据库
                   self.db.grouplist.insert(g)
           except  Exception, e:
               print e
               continue

   def GroupMsgStatistics(self,msg):
        #查询对应的群
        g=self.db.grouplist.find_one({'username':msg['FromUserName']})
        # print g
        if g!=None:
            #判断是否包含这个人的群信息(个人的昵称和群拼音)
            one=self.db.groupstatistics.find_one({'nickname':msg['ActualNickName'],'grouppy':g['grouppy']})
            if one==None:
                #新增这个人的信息
                s = dict(
                    nickname=msg['ActualNickName'].encode('utf-8'),
                    groupname=g['groupname'],
                    grouppy=g['grouppy'],
                    msgcount=1
                )
                s[msg['Type']]=1
                # print s
                self.db.groupstatistics.insert(s)
            else:
                #更新统计信息
                self.db.groupstatistics.update({'nickname':msg['ActualNickName'],'grouppy':g['grouppy']},
                                      { '$inc' : { 'msgcount' : 1,msg['Type']:1} },True)
