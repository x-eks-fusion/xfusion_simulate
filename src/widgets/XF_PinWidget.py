from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsView
from PySide6.QtGui import QColor, QPen, QBrush, QPainterPath
from PySide6.QtCore import Qt, QPointF
from enum import Enum
import logging

from widgets.XF_LineWidget import LineWidget

import uuid

"""
引脚控件
"""


class Pin(QGraphicsEllipseItem):
    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2
    VCC = 3
    GND = 4

    LEFT = 0
    RIGHT = 1

    def __init__(self, x, y, radius, pin_type, color, dir, parent=None):
        super().__init__(x, y, radius, radius, parent)
        self.uuid = uuid.uuid4()
        self.connection = []   # 当前连接的目标
        self.scene_pos = self.mapToScene(
            self.boundingRect().center())  # 获取当前位置
        self.pin_type = pin_type  # 引脚类型 (Input, Output, etc.)
        self._color = color
        self.setBrush(QBrush(QColor(color)))  # 设置颜色
        self.setPen(QPen(QColor("black")))  # 设置边框
        self.setFlags(
            QGraphicsEllipseItem.ItemIsSelectable  # 支持选中
        )
        self.setZValue(1)    # 图层置顶
        self._dir = dir
        self.parent = parent
        self._attribute = {"UUID": self.uuid.hex}  # 对外展示的属性
        self.connect_pin = []  # 连接的pin
        self.connect_line = []  # 连接的线段

        self._current_line = None
        self._start_pin = None

    def mousePressEvent(self, event):
        """按下Pin时，开始绘制线路"""
        if event.button() == Qt.LeftButton:
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            item = self.scene().itemAt(scene_pos, self.transform())  # 获取场景中的对象
            if isinstance(item, Pin):  # 点击的是起点Pin
                self._start_pin = item
                self._current_line = LineWidget(
                    self._start_pin, self._dir, self._color)
                self.scene().addItem(self._current_line)
                print("Scene items:", item, isinstance(item, Pin))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """拖动鼠标时动态绘制线路"""
        if self._current_line:  # 更新目标点为鼠标位置
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            self._current_line.set_des_point(scene_pos)
            self._current_line.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """释放鼠标时确定线路是否有效"""
        if self._current_line:
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            item = self.scene().itemAt(scene_pos, self.transform())  # 获取场景中的对象
            if isinstance(item, Pin) and item != self._start_pin:  # 放手时目标为Pin
                self._current_line.set_des_pin(item)
            else:  # 放手时目标不是Pin，删除当前连接
                self.scene().removeItem(self._current_line)
            self._current_line = None
            self._start_pin = None
        super().mouseReleaseEvent(event)

    def onMoved(self):
        self.scene_pos = self.mapToScene(
            self.boundingRect().center())

    @property
    def attribute(self) -> dict:
        self._attribute["sence_pos_x"] = self.scene_pos.x()
        self._attribute["sence_pos_y"] = self.scene_pos.y()
        self._attribute["is_connected"] = bool(len(self.connection)),
        return self._attribute


class InputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT, "purple", dir, parent=parent)
        self._attribute["type"] = "input"
        self._attribute["name"] = f"{parent.name}:{name}"


class OutputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.OUTPUT, "blue", dir, parent=parent)
        self._attribute["type"] = "output"
        self._attribute["name"] = f"{parent.name}:{name}"


class InputOutputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT_OUTPUT, "yellow", dir, parent=parent)
        self._attribute["type"] = "input_output"
        self._attribute["name"] = f"{parent.name}:{name}"


class GND(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.GND, "green", dir, parent=parent)
        self._attribute["type"] = "GND"
        self._attribute["name"] = f"{parent.name}:GND"


class VCC(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.VCC, "red", dir, parent=parent)
        self._attribute["type"] = "VCC"
        self._attribute["name"] = f"{parent.name}:VCC"
