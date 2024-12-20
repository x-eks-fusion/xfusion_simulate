from handlers.XF_BaseHandler import BaseHandler


class GPIOHandler(BaseHandler):
    def configHandler(self, config):
        super().configHandler(config)
        self.pin = config["id"] % 0x1000000
        self.direction = config["direction"]
        self.pull = config["pull"]
        self.speed = config["speed"]
        self.intr_enable = config["intr_enable"]
        self.intr_type = config["intr_type"]

    def reciveHandler(self, value):
        self.sendLevel(self.pin, value)

    def getHandler(self, response):
        if self.pull == 0:      # 浮空
            self.sendLevelRequest(self.pin, b'\xff')
        elif self.pull == 1:    # 上拉
            self.sendLevelRequest(self.pin, b'\x01')
        elif self.pull == 2:    # 下拉
            self.sendLevelRequest(self.pin, b'\x00')
        data = self.recv()
        return data["value"]
