#!/usr/bin/env python
#coding:utf8
import time
from dbaccess.selectdb import GetMsg,statistics

class HandleMsg():
    def splitlongmsg(self,msg):
        if(len(msg)>1000):
            return msg[0:1000]
        else:
            return msg
    def defaultmsghandle(self,msg):
        if(u'#帮助' in msg['Content']):
            dbmsg = GetMsg()
            hmsg=dbmsg.getDefaultMsgByMsgFlag('help')
            return hmsg['content']
        elif (u'#谁最能聊' in msg['Content'] or u'#谁最能BB' in msg['Content']):
            objstat = statistics()
            statist=objstat.getStatisticsbyGroupandType(msg,'all')
            i=1
            content=''
            for item in statist:
                print item
                content=content+u'第%s名:%s,共发消息:%s条\n'%(i,item['nickname'],item['msgcount'])
                i=i+1
            print content
            return content
        elif (u'#谁最爱发图' in msg['Content']):
            objstat = statistics()
            statist = objstat.getStatisticsbyGroupandType(msg, 'pic')
            i = 1
            content = ''
            for item in statist:
                print item
                try:
                    content = content + u'第%s名:%s,共发图片消息:%s条\n' % (i, item['nickname'], item['Picture'])
                    i = i + 1
                except  Exception, e:
                    print e
                    break
            print content
            return content
        else:
            return ''