from widgets.XF_DeviceWidget import Device
from widgets.XF_PinWidget import InputPin, OutputPin, VCCOut, Pin
from PySide6.QtCore import Qt, Signal
import logging


class Button(Device):
    button_path = [
        "src/svg/button/Button_off.svg",
        "src/svg/button/Button_on.svg"
    ]

    pressed = Signal(bool)

    def __init__(self, x, y, parent=None):
        super().__init__(x, y, "Button", 2,
                         svg_path="src/svg/button/Button_off.svg", parent=parent)
        # 添加引脚
        self.btn1 = InputPin("btn1", 0, 54, 10, Pin.LEFT, self)
        self.btn2 = InputPin("btn2", 0, 19, 10, Pin.LEFT, self)
        self.btn3 = InputPin("btn3", 128, 54, 10, Pin.RIGHT, self)
        self.btn4 = InputPin("btn4", 128, 19, 10, Pin.RIGHT, self)
        self.addPin(self.btn1)
        self.addPin(self.btn2)
        self.addPin(self.btn3)
        self.addPin(self.btn4)
        self._is_pressed = False
        self.input_level = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.press()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.release()
        super().mouseReleaseEvent(event)

    def press(self):
        self.loadSvg(self.button_path[1])
        self.update()
        self._is_pressed = True

    def release(self):
        self.loadSvg(self.button_path[0])
        self.update()
        self._is_pressed = False

    @property
    def attribute(self) -> dict:
        self._attribute = super().attribute
        self._attribute["status"] = self._is_pressed
        return self._attribute

    # 按钮的运行逻辑
    def onRunning(self, kwargs):
        type = kwargs["type"]

        # 如果是发送电平，则更新输入电平
        # 连通的引脚传输一样的电平
        if type == Device.DATA_TYPE_LEVEL_TRANSMIT:
            self.input_level = kwargs["value"]
            pin = kwargs["input"]["pin"]
            if pin == self.btn1:
                self.transmitData(
                    self.btn3, Device.DATA_TYPE_LEVEL_RESPOSE,
                    self.input_level)
            elif pin == self.btn2:
                self.transmitData(
                    self.btn4, Device.DATA_TYPE_LEVEL_RESPOSE,
                    self.input_level)
            elif pin == self.btn3:
                self.transmitData(
                    self.btn1, Device.DATA_TYPE_LEVEL_RESPOSE,
                    self.input_level)
            elif pin == self.btn4:
                self.transmitData(
                    self.btn2, Device.DATA_TYPE_LEVEL_RESPOSE,
                    self.input_level)

        # 如果是发送请求
        # 判断是否按下
        # 按下则返回输入电平
        # 否则返回请求端的电平
        if type != Device.DATA_TYPE_LEVEL_REQUEST:
            return
        pin = kwargs["input"]["pin"]
        level = kwargs["value"]
        if self._is_pressed:
            self.transmitData(
                pin, Device.DATA_TYPE_LEVEL_RESPOSE, self.input_level)
        else:
            self.transmitData(
                pin, Device.DATA_TYPE_LEVEL_RESPOSE, level)
