#coding:utf8
import time
import itchat
from dbaccess.storage2db import MsgInQueue
from dbaccess.storage2db import MsgOutQueue2db

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

    @itchat.msg_register('Friends')
    def add_friend(msg):
        itchat.add_friend(**msg['Text'])
        itchat.get_contract()
        itchat.send('Nice to meet you!', msg['RecommendInfo']['UserName'])

    @itchat.msg_register('Text', isGroupChat = True)
    def text_reply(msg):
        # print itchat.__client.storageClass.groupDict
        print itchat.__client.storageClass.chatroomList
        print msg
        # 实例化入队类
        inqueue=MsgInQueue(queue)
        # 消息入队
        inqueue.putmsgqueue(msg)
        if msg['isAt']:
            print msg
            itchat.send(u'@%s\u2005I received: %s'%(msg['ActualNickName'], msg['Content']), msg['FromUserName'])

    itchat.run()

if __name__ == '__main__':
    itchat.auto_login(hotReload = True)
    # simple_reply()
    complex_reply()
