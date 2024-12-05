from widgets.XF_DeviceWidget import Device
from widgets.XF_PinWidget import VCCOut, GNDOut, Pin, InputOutputPin


class MCU(Device):
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, "MCU", 2,
                         svg_path="src/svg/MCU.svg", parent=parent)
        # 添加引脚
        self.vcc = VCCOut(3, 52, 10, Pin.LEFT, self)       # VCC 引脚
        self.gnd = GNDOut(191, 52, 10, Pin.RIGHT, self)       # GND 引脚
        self.addPin(self.vcc)
        self.addPin(self.gnd)
        self.pin = []
        for i in range(1, 19):
            pin = InputOutputPin(
                f"P{i}", 3, 52+18.7*i, 10, Pin.LEFT, self)
            self.pin.append(pin)
            self.addPin(pin)
        for i in range(19, 37):
            pin = InputOutputPin(
                f"P{i}", 191, 52+18.7*(i-18), 10, Pin.RIGHT, self)
            self.pin.append(pin)
            self.addPin(pin)
