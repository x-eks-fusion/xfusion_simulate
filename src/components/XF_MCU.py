from widgets.XF_ComponentWidget import Component
from widgets.XF_PinWidget import VCCOut, GNDIn, Pin


class MCU(Component):
    def __init__(self, x, y, parent=None):
        super().__init__(x, y, "MCU", 2,
                         svg_path="src/svg/MCU.svg", parent=parent)
        # 添加引脚
        self.addPin(VCCOut(3, 52, 10, Pin.LEFT, self))       # VCC 引脚
        self.addPin(GNDIn(191, 52, 10, Pin.RIGHT, self))       # GND 引脚
        # self.addPin(InputPin(10, 70, 10))  # Input 引脚
        # self.addPin(OutputPin(10, 100, 10))  # Output 引脚
