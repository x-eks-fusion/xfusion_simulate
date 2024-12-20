from handlers.XF_BaseHandler import BaseHandler


class SPIHandler(BaseHandler):
    def configHandler(self, config):
        print("spiConfigHandler")

    def getHandler(self, response):
        print("spiSendHandler")
        return b''

    def reciveHandler(self, value):
        print("spiReciveHandler")
