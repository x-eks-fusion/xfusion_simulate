from handlers.XF_BaseHandler import BaseHandler


class I2CHandler(BaseHandler):
    def configHandler(self, config):
        print("i2cConfigHandler")

    def getHandler(self, response):
        print("i2cSendHandler")
        return b''

    def reciveHandler(self, value):
        print("i2cReciveHandler")