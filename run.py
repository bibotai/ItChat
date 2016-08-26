#coding:utf8
import time
import itchat
from dbaccess.storage2db import MsgInQueue
from dbaccess.storage2db import MsgOutQueue2db
from dbaccess.storage2db import Storage2DB
from dbaccess.selectdb import GetMsg
import tools.msgHandle
import xml.etree.ElementTree as Etree

from Queue import Queue


def simple_reply():
    @itchat.msg_register
    def simple_reply(msg):
        if msg.get('Type', '') == 'Text':
            return 'I received: %s'%msg.get('Content', '')
    itchat.run()

def complex_reply():
    queue = Queue()
    # 实例化出队入库类
    outqueue = MsgOutQueue2db(queue)
    # 开启线程
    outqueue.start()
    @itchat.msg_register(['Text', 'Map', 'Card', 'Note', 'Sharing'])
    def text_reply(msg):
        itchat.send('%s: %s'%(msg['Type'], msg['Text']), msg['FromUserName'])

    @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'])
    def download_files(msg):
        fileDir = '%s%s'%(msg['Type'], int(time.time()))
        msg['Text'](fileDir)
        itchat.send('%s received'%msg['Type'], msg['FromUserName'])
        itchat.send('@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', fileDir), msg['FromUserName'])

    # @itchat.msg_register('Friends')
    # def add_friend(msg):
    #     itchat.add_friend(**msg['Text'])
    #     itchat.get_contract()
    #     itchat.send('Nice to meet you!', msg['RecommendInfo']['UserName'])


    #群




    #处理群文字消息
    @itchat.msg_register('Text', isGroupChat = True)
    def text_reply(msg):
        # print msg
        # 实例化入队类
        inqueue=MsgInQueue(queue)
        # 消息入队
        inqueue.putmsgqueue(msg)
        nickname = itchat.__client.storageClass.nickName
        if msg['isAt'] or '@%s'%(nickname) in msg['Content']:
            try:
                import plugin.tuling as tuling
                r = tuling.get_response(msg['Content'].replace('@%s'%(nickname),'').strip())
                itchat.send(u'\u2005%s' % (r), msg['FromUserName'])
            except        Exception, e:
                print e

        else:
            # 处理特定字符串
            try:
                hanmsg = tools.msgHandle.HandleMsg()
                remsg = hanmsg.defaultmsghandle(msg)
                if(remsg!=''):
                    print 'if(remsg!=''):'
                    itchat.send(u'\u2005%s ' % (remsg), msg['FromUserName'])
            except        Exception, e:
                print e
    #处理位置消息
    @itchat.msg_register('Map',isGroupChat=True)
    def map_reply(msg):
        try:
            # print msg
            inqueue = MsgInQueue(queue)
            inqueue.putmsgqueue(msg)
            index=msg['Content'].find(':')
            msg['Content']=msg[0:index]
            itchat.send(u'@%s\u2005你是不是在这里!%s' % (msg['ActualNickName'],msg['Content']), msg['FromUserName'])
        except  Exception, e:
            print e
    #处理系统消息
    @itchat.msg_register('Note', isGroupChat=True)
    def map_reply(msg):
        try:
            inqueue = MsgInQueue(queue)
            inqueue.putmsgqueue(msg)
            #新人入群
            indexs=msg['Content'].find(u'邀请')
            indexe=msg['Content'].find(u'加入')
            if(indexs>0):
                print  indexs
                print  indexe
                newmembername=msg['Content'][indexs+2:indexe]
                itchat.send(u'\u2005欢迎新人"%s"入群👏👏' % (newmembername), msg['FromUserName'])
                time.sleep(1)
                hanmsg = tools.msgHandle.HandleMsg()
                m=hanmsg.defaultgroupmsghandle(msg,'newmember')
                itchat.send(u'\u2005@%s %s' % (newmembername,m), msg['FromUserName'])
        except  Exception, e:
            print e
        else:
            #撤回
            try:
                if(msg['MsgType']==10002):
                    # print msg
                    dbmsg = GetMsg()
                    data_tree = Etree.fromstring(msg['Content'].encode('utf-8'))
                    print data_tree
                    msgid = data_tree.find('revokemsg/msgid').text
                    print msg['ActualUserName'],msg['FromUserName'],msgid
                    revokmsg=dbmsg.getrevokemsg(msg['ActualUserName'],msg['FromUserName'],msgid)
                    print revokmsg
                    if(revokmsg!=None):
                        if (revokmsg['type'] == 'Picture' or revokmsg['type'] == 'Recording' or
                                    revokmsg['type'] == 'Attachment' or revokmsg['type'] == 'Video'):

                            itchat.send(u'\u2005@%s 撤回了一条消息,撤回的消息是:' % (msg['ActualNickName']), msg['FromUserName'])
                            time.sleep(2)
                            print revokmsg['message'],revokmsg['type']
                            itchat.send('@%s@%s' % ('img' if revokmsg['type'] == 'Picture' else 'fil', revokmsg['message']),
                                        msg['FromUserName'])
                        else:
                            hanmsg=tools.msgHandle.HandleMsg()
                            remsg=hanmsg.splitlongmsg(revokmsg['message'])
                            itchat.send(u'\u2005@%s 撤回了一条消息,撤回的消息是:%s ' % (msg['ActualNickName'],remsg), msg['FromUserName'])
            except  Exception, e:
                print e
    #处理图片,语音,视频,附件
    @itchat.msg_register(['Picture', 'Recording', 'Attachment', 'Video'], isGroupChat=True)
    def download_files(msg):
        #print msg
        dir=''
        if(msg['Type']=='Picture'):
            dir='picture'
        elif(msg['Type']=='Recording'):
            dir = 'recording'
        elif(msg['Type']=='Attachment'):
            dir = 'attachment'
        elif(msg['Type']=='Video'):
            dir = 'video'
        fileDir = 'storage/%s/%s%s' % (dir,msg['Type'], int(time.time()))
        print fileDir
        msg['Content']=fileDir
        inqueue = MsgInQueue(queue)
        inqueue.putmsgqueue(msg)
        msg['Text'](fileDir)
        # Todo:斗图
        # itchat.send('%s received' % msg['Type'], msg['FromUserName'])
        # itchat.send('@%s@%s' % ('img' if msg['Type'] == 'Picture' else 'fil', fileDir), msg['FromUserName'])

    itchat.run()

def initGroup():
    groupList=itchat.__client.storageClass.chatroomList
    db=Storage2DB()
    db.storageGroupName(groupList)
    db.InitDefaultMessage()

if __name__ == '__main__':
    itchat.auto_login(hotReload = True,enableCmdQR=2)
    initGroup()
    # simple_reply()
    complex_reply()
