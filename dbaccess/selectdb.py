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
        return msgs
    def getDefaultMsgByMsgFlag(self,flag):
        msg=self.db.defaultmsg.find_one({'msgflag':flag})
        return msg