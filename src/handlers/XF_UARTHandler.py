from handlers.XF_BaseHandler import BaseHandler


class UARTHandler(BaseHandler):
    def configHandler(self, config):
        print("uartConfigHandler")

    def getHandler(self, response):
        print("uartSendHandler")
        return b''

    def reciveHandler(self, value):
        print("uartReciveHandler")
