#!/usr/bin/env python
#coding:utf8
import time
from dbaccess.selectdb import GetMsg
class HandleMsg():
    def splitlongmsg(self,msg):
        if(len(msg)>1000):
            return msg[0:1000]
        else:
            return msg
    def defaultmsghandle(self,msg,):
        if(u'#帮助' in msg):
            print ''
            dbmsg = GetMsg()
            msg=dbmsg.getDefaultMsgByMsgFlag('help')
            return msg['content']
        else:
            return ''