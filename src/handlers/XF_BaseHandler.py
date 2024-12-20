import queue


send = queue.Queue()
recv = queue.Queue()


class BaseHandler:
    MSG_TYPE_LEVEL_TRANSMIT = 0
    MSG_TYPE_LEVEL_REQUEST = 1
    MSG_TYPE_LEVEL_RESPOSE = 2
    MSG_TYPE_DATA_TRANSMIT = 3
    MSG_TYPE_DATA_RECEIVE = 4

    def __init__(self):
        self.config = {}

    def configHandler(self, config):
        self.config = config.copy()
        self.pin = -1

    def getHandler(self, response):
        return b""

    def reciveHandler(self, value):
        pass

    def sendLevel(self, pin, value):
        send.put({"pin": pin, "value": value,
                 "type": BaseHandler.MSG_TYPE_LEVEL_TRANSMIT})

    def sendLevelRequest(self, pin, level):
        send.put({"pin": pin, "value": level,
                 "type": BaseHandler.MSG_TYPE_LEVEL_REQUEST})

    def sendData(self, pin, value):
        send.put({"pin": pin, "value": value,
                 "type": BaseHandler.MSG_TYPE_DATA_TRANSMIT})

    def recv(self):
        return recv.get()
