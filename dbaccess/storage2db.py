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
        # print 'put msg in queue success:'+msg['Content']

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
                # print "%s: %s get %s from queue !" % (time.ctime(), self.getName(), msg['Content'].encode('utf-8'))
                try:
                    #格式化消息数据
                    m = dict(groupname=msg['FromUserName'].encode('utf-8'),
                             time=msg['CreateTime'],
                             username=msg['ActualUserName'],
                             usernickname=msg['ActualNickName'].encode('utf-8'),
                             message=msg['Content'].encode('utf-8'),
                             messagetype=msg['MsgType'],
                             type=msg['Type'],
                             msgid=msg['MsgId']
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
            #更新统计信息
            self.db.groupstatistics.update({'nickname':msg['ActualNickName'],'grouppy':g['grouppy']},
                                  { '$inc' : { 'msgcount' : 1,msg['Type']:1} },True)

   def InitDefaultMessage(self):
        m1=self.db.defaultmsg.find_one({'msgflag': 'help'})
        if m1==None:
            m= dict(msgflag='help',
                    content='小图群聊机器人\n'+
                            '支持功能：\n'+
                            '*生活助手类*\n'+
                            '***注意，此类别的所有消息均要@我发送！***\n'+
                            '1、聊天：@我并加入聊天内容\n'+
                            '2、找图片:如小狗图片，要包含“图片”\n'+
                            '3、找新闻:如今日新闻，要包含“新闻”\n'+
                            '4、查列车:如6月1号深圳到厦门的列车，时间+出发地+目的地\n'+
                            '5、查航班:如6月1号深圳到上海的飞机，同上\n'+
                            '6、查菜谱:如土豆焖鸡怎么做\n'+
                            '7、查快递:如顺丰 12345678\n'+
                            '8、查天气:如北京天气\n'+
                            '9、成语接龙:如成语接龙\n'+
                            '更多功能自己发现😂\n'+
                            '*防撤回类*\n'+
                            '文字,图片,视频,附件均可防撤回\n'+
                            '*群聊统计类*\n'+
                            '1、#谁最能聊\n'+
                            '2、#谁最爱发图\n' +
                            '3、#谁最爱发语音\n' +
                            '4、#谁最爱发视频\n'
                    )
            self.db.defaultmsg.insert(m)

        m2=self.db.defaultmsg.find_one({'grouppy': 'ichunqiuxinxianquanmofaxueyuan'})
        if m2==None:
            m= dict(grouppy='ichunqiuxinxianquanmofaxueyuan',
                    newmember='这里是"i春秋-信息安全魔法学院"\n'+
                    '进群发红包，发果照，报三围。\n'+
                    '温馨提示:请给手机多充一点流量。\n\n'+
                    '关注i春秋微信公众号icqedu'+
                    '关注i春秋微博@i春秋学院' +
                    '注册成为i春秋会员：www.ichunqiu.com/mobile'
                    )
            self.db.defaultmsg.insert(m)
        m3 = self.db.defaultmsg.find_one({'grouppy': 'zuosiceshiqun'})
        if m3 == None:
            m = dict(grouppy='zuosiceshiqun',
                     newmember='这里是作死测试群"\n'
                     )
            self.db.defaultmsg.insert(m)
        m4 = self.db.defaultmsg.find_one({'grouppy': 'baimaohuishililiaomeijiaoxuequn'})
        if m4 == None:
            m = dict(grouppy='baimaohuishililiaomeijiaoxuequn',
                     newmember='这里是【白帽汇】实力撩妹教学群"\n' +
                               '进群发红包，发果照，报三围。\n' +
                               '缪缪是世界上最漂亮的人。\n\n' +
                               '缪缪是最强王者!'
                     )
            self.db.defaultmsg.insert(m)
        m5 = self.db.defaultmsg.find_one({'grouppy': 'SOBUGcaidanfuliqun'})
        if m5 == None:
            m = dict(grouppy='SOBUGcaidanfuliqun',
                     newmember='这里是 SOBUG彩蛋福利群"\n' +
                               '进群发红包，发果照，报三围。\n\n' +
                               '欢迎去SOBUG提交漏洞!https://www.sobug.com'
                     )
            self.db.defaultmsg.insert(m)
        m6 = self.db.defaultmsg.find_one({'grouppy': 'anquanjuanyanzhidandangqunspanclassemojiemoji1f493span'})
        if m6 == None:
            m = dict(grouppy='anquanjuanyanzhidandangqunspanclassemojiemoji1f493span',
                     newmember='这里是 安全圈颜值担当群💓"\n' +
                               '进群发红包，发果照，报三围。\n\n' +
                               '文明聊(yue)天(pao)'
                     )
            self.db.defaultmsg.insert(m)
        m7 = self.db.defaultmsg.find_one({'grouppy': 'anquanjuanyanzhidandangqunspanclassemojiemoji1f493span'})
        if m7 == None:
            m = dict(grouppy='anquanjuandeanquan2qun',
                     newmember='这里是 安全圈的安全2群💓"\n' +
                               '进群发红包，发果照，报三围。\n' +
                               '欢迎关注安全圈微信公众号\n'+
                               '程程好漂亮!'
                     )
            self.db.defaultmsg.insert(m)

