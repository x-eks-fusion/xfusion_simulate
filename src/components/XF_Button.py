from widgets.XF_ComponentWidget import Component
from widgets.XF_PinWidget import InputPin, OutputPin, VCCOut, Pin


class Button(Component):
    button_path = [
        "src/svg/button/Button_off.svg",
        "src/svg/button/Button_on.svg"
    ]

    def __init__(self, x, y, parent=None):
        super().__init__(x, y, "MCU", 2,
                         svg_path="src/svg/button/Button_off.svg", parent=parent)
        # 添加引脚
        self.addPin(InputPin("btn1", 0, 54, 10, Pin.LEFT, self))
        self.addPin(OutputPin("btn2", 0, 19, 10, Pin.LEFT, self))
        self.addPin(OutputPin("btn3", 128, 54, 10, Pin.RIGHT, self))
        self.addPin(InputPin("btn4", 128, 19, 10, Pin.RIGHT, self))
        self._is_pressed = False

    def press(self):
        self.loadSvg(self.button_path[1])
        self._is_pressed = True

    def release(self):
        self.loadSvg(self.button_path[0])
        self._is_pressed = False

    @property
    def attribute(self) -> dict:
        self._attribute = super().attribute
        self._attribute["status"] = self._is_pressed
        return self._attribute
