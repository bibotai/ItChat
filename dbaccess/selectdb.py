#!/usr/bin/env python
#coding:utf8
import threading,time,pymongo
from pymongo import MongoClient
class GetMsg():
    def __init__(self):
        # 建立MongoDB连接
        self.conn = MongoClient()
        # 数据库
        self.db = self.conn.wechatRobot
    def getLastMsgByUsernameGroupusername(self,username,groupname,limit):
        msgs=self.db.messages.find({"$and": [{"username": username},
                                             {"groupname":groupname},
                                             {"type": {"$ne": "Note"}}]}).sort([('time', -1)]).limit(limit)

    def getrevokemsg(self,username,groupname,msgid):
        msg=self.db.messages.find_one({"$and": [{"username": username},
                                      {"groupname": groupname},
                                      {"msgid":msgid}]})
        return msg
    def getDefaultMsgByMsgFlag(self,flag):
        msg=self.db.defaultmsg.find_one({'msgflag':flag})
        return msg

class statistics():
    def __init__(self):
        # 建立MongoDB连接
        self.conn = MongoClient()
        # 数据库
        self.db = self.conn.wechatRobot
    def getStatisticsbyGroupandType(self,msg,type):
        # 查询对应的群
        print msg
        g = self.db.grouplist.find_one({'username': msg['FromUserName']})
        if g != None:
            if(type=='all'):
                stat = self.db.groupstatistics.find({'grouppy': g['grouppy']}).sort([('msgcount', -1)]).limit(20)
                return stat
            if(type=='pic'):
                stat = self.db.groupstatistics.find({'grouppy': g['grouppy']}).sort([('Picture', -1)]).limit(20)
                return stat
            if (type == 'rec'):
                stat = self.db.groupstatistics.find({'grouppy': g['grouppy']}).sort([('Recording', -1)]).limit(20)
                return stat
            if (type == 'video'):
                stat = self.db.groupstatistics.find({'grouppy': g['grouppy']}).sort([('Video', -1)]).limit(20)
                return stat
