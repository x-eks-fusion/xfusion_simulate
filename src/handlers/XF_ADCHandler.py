from handlers.XF_BaseHandler import BaseHandler


class ADCHandler(BaseHandler):
    def configHandler(self, config):
        print("adcConfigHandler")

    def getHandler(self, response):
        print("adcSendHandler")
        return b''

    def reciveHandler(self, value):
        print("adcReciveHandler")
