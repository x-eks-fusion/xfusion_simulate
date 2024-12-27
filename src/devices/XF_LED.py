from widgets.XF_DeviceWidget import Device
from widgets.XF_PinWidget import InputPin, OutputPin, Pin
import logging


class LED(Device):
    color_path = {
        "off": "src/svg/LED/LED_off.svg",
        "red": "src/svg/LED/LED_red.svg",
        "orange": "src/svg/LED/LED_orange.svg",
        "yellow": "src/svg/LED/LED_yellow.svg",
        "green": "src/svg/LED/LED_green.svg",
        "cyan": "src/svg/LED/LED_cyan.svg",
        "blue": "src/svg/LED/LED_blue.svg",
        "purple": "src/svg/LED/LED_purple.svg",
    }

    def __init__(self, color="red"):
        if color not in self.color_path.keys():
            raise ValueError("no led color support")
        self.color = color
        super().__init__("LED", 2, self.color_path["off"])
        # 添加引脚
        self.addPin(InputPin("negative", 25, 80, 10, Pin.DOWN, self))
        self.addPin(InputPin("positive", 45, 80, 10, Pin.RIGHT, self))
        self.negative_level = -1
        self.positive_level = -1
        self.is_on = False
        # self.setVerticalMirror()

    def on(self):
        self.is_on = True
        self.loadSvg(self.color_path[self.color])

    def off(self):
        self.is_on = False
        self.loadSvg(self.color_path["off"])

    def toggle(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.loadSvg(self.color_path[self.color])
        else:
            self.loadSvg(self.color_path["off"])

    def setColor(self, color):
        if color not in self.color_path.keys():
            raise ValueError("no led color support")
        self.loadSvg(self.color_path[color])

    @property
    def attribute(self) -> dict:
        self._attribute = super().attribute
        self._attribute["status"] = self.is_on
        self._attribute["color"] = self.color
        return self._attribute

    # LED的运行逻辑
    def onRunning(self, kwargs):
        # 如果是发送电平，更新输入电平
        logging.debug(f"{self.positive_level}, {self.positive_level}")
        type = kwargs["type"]
        if type == Device.MSG_TYPE_LEVEL_REQUEST:
            pin = kwargs["input"]["pin"]
            level = kwargs["value"]
            self.transmitData(pin, Device.MSG_TYPE_LEVEL_RESPOSE, level)
        if type != Device.MSG_TYPE_LEVEL_TRANSMIT:
            return
        pin = kwargs["input"]["pin"]
        if pin == self.pins["positive"]:
            self.positive_level = kwargs["value"]
        elif pin == self.pins["negative"]:
            self.negative_level = kwargs["value"]
        # 根据电平判断 LED 状态, 只有正极高电平，负极低电平，LED亮
        if self.positive_level == b'\x01' and self.negative_level == b'\x00':
            self.on()
        else:
            self.off()
