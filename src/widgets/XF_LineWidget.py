from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QApplication
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsItem, QGraphicsPathItem, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
import sys
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsDropShadowEffect, QGraphicsItem
from PySide6.QtGui import QColor, QPen, QPainter, QPainterPath
from PySide6.QtCore import Qt, QPointF
import logging


import uuid


class LineWidget(QGraphicsPathItem):
    LEFT = 0
    RIGHT = 1

    def __init__(self, start_pin, dir, color='#ff0000', parent=None):

        super().__init__(parent)

        self._start_pin = start_pin
        self._dir = dir
        self._start_pos = start_pin.scene_pos
        self._des_pos = self._start_pos

        # 初始画笔
        self._color = color
        self._pen_default = QPen(QColor(self._color))
        self._pen_default.setWidthF(2)

        self.setZValue(-1)

        self._id = uuid.uuid4()

        # 选中投影
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(20)

        self._shadow_color = QColor(self._color)
        self._attribute = {"UUID": self._id.hex, "name": "line"}

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        logging.info("曲线创建成功")

    def 

    def set_des_point(self, des_pos):
        self._des_pos = des_pos

    def set_des_pin(self, des_pin):
        self._des_pin = des_pin
        self._des_pos = self._des_pin.scene_pos

    def paint(self, painter: QPainter, option, widget):
        self.prepareGeometryChange()
        self.update_path()

        painter.setPen(self._pen_default)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

        if self.isSelected():
            self._shadow.setColor(self._shadow_color)
            self.setGraphicsEffect(self._shadow)
        else:
            self._shadow.setColor('#00000000')
            self.setGraphicsEffect(self._shadow)

    # 更新路径
    def update_path(self):
        self._start_pos = self._start_pin.scene_pos

        path = QPainterPath(self._start_pos)

        xwidth = self._start_pos.x()-self._des_pos.x()

        xwidth = xwidth+0.01 if xwidth == 0 else xwidth

        yheight = abs(self._start_pos.y()-self._des_pos.y())

        tangent = float(yheight)/xwidth*0.5

        tangent *= xwidth

        if xwidth > 0:
            if xwidth > 150:
                xwidth = 150
            if self._dir == self.RIGHT:
                tangent += xwidth
        else:
            if tangent > 150:
                tangent = 150
            if self._dir == self.LEFT:
                tangent -= xwidth

        if self._dir == self.LEFT:
            path.cubicTo(QPointF(self._start_pos.x()-tangent, self._start_pos.y()),
                         QPointF(self._des_pos.x()+tangent, self._des_pos.y()),
                         self._des_pos)
        elif self._dir == self.RIGHT:
            path.cubicTo(QPointF(self._start_pos.x()+tangent, self._start_pos.y()),
                         QPointF(self._des_pos.x()-tangent, self._des_pos.y()),
                         self._des_pos)
        self.setPath(path)

    @property
    def attribute(self):
        return self._attribute
