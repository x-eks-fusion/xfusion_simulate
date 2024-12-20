from handlers.XF_BaseHandler import BaseHandler


class DACHandler(BaseHandler):
    def configHandler(self, config):
        print("dacConfigHandler")

    def getHandler(self, response):
        print("dacSendHandler")
        return b''

    def reciveHandler(self, value):
        print("dacReciveHandler")
