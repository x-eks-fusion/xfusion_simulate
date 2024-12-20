from handlers.XF_BaseHandler import BaseHandler


class TimerHandler(BaseHandler):
    def configHandler(self, config):
        print("timerConfigHandler")

    def getHandler(self, response):
        print("timerSendHandler")
        return b''

    def reciveHandler(self, value):
        print("timerReciveHandler")
