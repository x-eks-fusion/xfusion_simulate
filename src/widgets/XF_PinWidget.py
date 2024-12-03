from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import Qt

from widgets.XF_LineWidget import LineWidget

import uuid
import logging

"""
引脚控件
"""


class Pin(QGraphicsEllipseItem):
    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2

    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def __init__(self, x, y, radius, pin_type, color, dir, parent=None):
        super().__init__(x, y, radius, radius, parent)
        self.uuid = uuid.uuid4()
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
        self._original_dir = dir
        self.parent = parent
        self._attribute = {"UUID": self.uuid.hex}  # 对外展示的属性
        self.connect_pins = []  # 连接的pin
        self.connect_lines = []  # 连接的线段

        self._current_line = None
        self._start_pin = None

    def setVerticalMirror(self):
        if self._original_dir == self.LEFT:
            self._dir = self.RIGHT
        elif self._original_dir == self.RIGHT:
            self._dir = self.LEFT

    def setHorizontalMirror(self):
        if self._original_dir == self.UP:
            self._dir = self.DOWN
        elif self._original_dir == self.DOWN:
            self._dir = self.UP

    def setAllMirror(self):
        if self._original_dir == self.LEFT:
            self._dir = self.RIGHT
        elif self._original_dir == self.RIGHT:
            self._dir = self.LEFT
        elif self._original_dir == self.UP:
            self._dir = self.DOWN
        elif self._original_dir == self.DOWN:
            self._dir = self.UP

    def setNoMirror(self):
        self._dir = self._original_dir

    def setRota(self, angle: float) -> None:
        if angle == 90:
            if self._original_dir == self.LEFT:
                self._dir = self.UP
            elif self._dir == self.RIGHT:
                self._dir = self.DOWN
            elif self._dir == self.UP:
                self._dir = self.RIGHT
            elif self._dir == self.DOWN:
                self._dir = self.LEFT
        elif angle == 180:
            if self._original_dir == self.LEFT:
                self._dir = self.RIGHT
            elif self._dir == self.RIGHT:
                self._dir = self.LEFT
            elif self._dir == self.UP:
                self._dir = self.DOWN
            elif self._dir == self.DOWN:
                self._dir = self.UP
        elif angle == 270:
            if self._original_dir == self.LEFT:
                self._dir = self.DOWN
            elif self._dir == self.RIGHT:
                self._dir = self.UP
            elif self._dir == self.UP:
                self._dir = self.LEFT
            elif self._dir == self.DOWN:
                self._dir = self.RIGHT
        else:
            self._dir = self._original_dir

    def mousePressEvent(self, event):
        """按下Pin时，开始绘制线路"""
        if event.button() == Qt.LeftButton:
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            item = self.scene().itemAt(scene_pos, self.transform())  # 获取场景中的对象
            if isinstance(item, Pin) and \
                    (item.pin_type == self.OUTPUT or item.pin_type == self.INPUT_OUTPUT):  # 点击的是起点Pin
                self._start_pin = item
                self._current_line = LineWidget(
                    self._start_pin, self._dir, self._color)
                self.scene().addItem(self._current_line)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """拖动鼠标时动态绘制线路"""
        if self._current_line:  # 更新目标点为鼠标位置
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            item = self.scene().itemAt(scene_pos, self.transform())  # 获取场景中的对象
            if isinstance(item, Pin) and item.parent != self._start_pin.parent and \
                    (item.pin_type == self.INPUT or item.pin_type == self.INPUT_OUTPUT):  # 放手时目标为Pin
                self._current_line.setEndDir(item.getDir())
            self._current_line.setEndPoint(scene_pos)
            self._current_line.updatePath()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """释放鼠标时确定线路是否有效"""
        if self._current_line:
            scene_pos = event.scenePos()  # 使用 scenePosition 获取位置
            item = self.scene().itemAt(scene_pos, self.transform())  # 获取场景中的对象
            if isinstance(item, Pin) and item.parent != self._start_pin.parent and \
                    (item.pin_type == self.INPUT or item.pin_type == self.INPUT_OUTPUT):  # 放手时目标为Pin
                self._current_line.setEndPin(item)
                self.connect_lines.append(self._current_line)
                self._current_line.setEndDir(item.getDir())
                item.connect_lines.append(self._current_line)
                item.connect_pins.append(self)
                self.connect_pins.append(item)
            else:  # 放手时目标不是Pin，删除当前连接
                self.scene().removeItem(self._current_line)

            self._current_line = None
            self._start_pin = None
        super().mouseReleaseEvent(event)

    def removeLine(self, line):
        for connect_line in self.connect_lines:
            if connect_line == line:
                self.scene().removeItem(connect_line)
                self.connect_lines.remove(connect_line)

    def removeAllLines(self):
        for connect_pin in self.connect_pins:
            for connect_line in self.connect_lines:
                connect_pin.removeLine(connect_line)
        self.connect_lines.clear()

    def onMoved(self):
        self.scene_pos = self.mapToScene(
            self.boundingRect().center())
        for i in self.connect_lines:
            i.updatePath()

    def getDir(self):
        return self._dir

    def getLines(self):
        return self.connect_lines

    @property
    def attribute(self) -> dict:
        self._attribute["sence_pos_x"] = self.scene_pos.x()
        self._attribute["sence_pos_y"] = self.scene_pos.y()
        self._attribute["is_connected"] = bool(len(self.connect_pins)),
        return self._attribute


class InputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT, "purple", dir, parent=parent)
        self._attribute["type"] = "input"
        self._attribute["name"] = name


class OutputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.OUTPUT, "blue", dir, parent=parent)
        self._attribute["type"] = "output"
        self._attribute["name"] = name


class InputOutputPin(Pin):
    def __init__(self, name, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT_OUTPUT, "yellow", dir, parent=parent)
        self._attribute["type"] = "input_output"
        self._attribute["name"] = name


class GNDOut(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.OUTPUT, "green", dir, parent=parent)
        self._attribute["type"] = "output"
        self._attribute["name"] = "GND"


class GNDIn(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT, "green", dir, parent=parent)
        self._attribute["type"] = "input"
        self._attribute["name"] = "GND"


class VCCOut(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.OUTPUT, "red", dir, parent=parent)
        self._attribute["type"] = "output"
        self._attribute["name"] = "VCC"


class VCCIn(Pin):
    def __init__(self, x, y, radius, dir, parent=None):
        super().__init__(x, y, radius, Pin.INPUT, "red", dir, parent=parent)
        self._attribute["type"] = "input"
        self._attribute["name"] = "VCC"
