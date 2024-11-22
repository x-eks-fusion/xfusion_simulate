from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QColor, QPen, QBrush
from enum import Enum

"""
引脚控件
"""


class PinType(Enum):
    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2
    VCC = 3
    GND = 4


class Pin(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, pin_type: PinType, color, parent=None):
        super().__init__(x, y, radius, radius, parent)
        self.pin_type = pin_type  # 引脚类型 (Input, Output, etc.)
        self.setBrush(QBrush(QColor(color)))  # 设置颜色
        self.setPen(QPen(QColor("black")))  # 设置边框
        self.connection = None  # 当前连接的目标
        self.setZValue(9999)


class InputPin(Pin):
    def __init__(self, x, y, radius, parent=None):
        super().__init__(x, y, radius, PinType.INPUT, "purple", parent)


class OutputPin(Pin):
    def __init__(self, x, y, radius, parent=None):
        super().__init__(x, y, radius, PinType.OUTPUT, "blue", parent)


class InputOutputPin(Pin):
    def __init__(self, x, y, radius, parent=None):
        super().__init__(x, y, radius, PinType.INPUT_OUTPUT, "yellow", parent)


class GND(Pin):
    def __init__(self, x, y, radius, parent=None):
        super().__init__(x, y, radius, PinType.GND, "green", parent)


class VCC(Pin):
    def __init__(self, x, y, radius, parent=None):
        super().__init__(x, y, radius, PinType.VCC, "red", parent)
