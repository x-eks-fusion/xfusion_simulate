from handlers.XF_BaseHandler import BaseHandler


class PWMHandler(BaseHandler):
    def configHandler(self, config):
        print("pwmConfigHandler")

    def getHandler(self, response):
        print("pwmSendHandler")
        return b''

    def reciveHandler(self, value):
        print("pwmReciveHandler")
