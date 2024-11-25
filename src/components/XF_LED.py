from widgets.XF_ComponentWidget import Component
from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtCore import Qt
from svgpathtools import svg2paths
from PySide6.QtGui import QPainterPath
from widgets.XF_PinWidget import InputPin, OutputPin, Pin


class LED(Component):
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

    def __init__(self, x, y, color="red", parent=None):
        if color not in self.color_path.keys():
            raise ValueError("no led color support")
        self.color = color
        super().__init__(x, y, "LED", 2, self.color_path["off"], parent=parent)
        # 添加引脚
        self.add_pin(InputPin("-", 45, 80, 10, Pin.RIGHT, self))
        self.add_pin(OutputPin("+", 25, 80, 10, Pin.LEFT, self))
        self.is_on = False

    def on(self):
        self.is_on = True
        self.load_svg(self.color_path[self.color])

    def off(self):
        self.is_on = False
        self.load_svg(self.color_path["off"])

    def toggle(self):
        self.is_on = not self.is_on
        if self.is_on:
            self.load_svg(self.color_path[self.color])
        else:
            self.load_svg(self.color_path["off"])

    def set_color(self, color):
        if color not in self.color_path.keys():
            raise ValueError("no led color support")
        self.load_svg(self.color_path[color])

    @property
    def attribute(self) -> dict:
        self._attribute["status"] = self.is_on
        self._attribute["color"] = self.color
        return self._attribute
