from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPointF
import logging


class LineWidget(QGraphicsPathItem):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

    def __init__(self, start_pin, dir, color='#ff0000', parent=None):

        super().__init__(parent)

        self._start_pin = start_pin
        self._dir = dir
        self._start_pos = start_pin.scene_pos
        self._end_pin = None
        self._end_pos = self._start_pos
        if self._dir == self.LEFT:
            self._end_dir = self.RIGHT
        elif self._dir == self.RIGHT:
            self._end_dir = self.LEFT
        elif self._dir == self.UP:
            self._end_dir = self.DOWN
        elif self._dir == self.DOWN:
            self._end_dir = self.UP

        # 初始画笔
        self._color = color
        self._pen_default = QPen(QColor(self._color))
        self._pen_default.setWidthF(5)

        self.setZValue(-1)

        # 选中投影
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(50)
        self._shadow_color = QColor(self._color)
        self._shadow_color.setAlpha(255)

        self.setFlags(QGraphicsItem.ItemIsSelectable)
        logging.info("曲线创建成功")

    def setEndPoint(self, end_pos):
        self._end_pos = end_pos

    def setEndPin(self, end_pin):
        self._end_pin = end_pin

    def setEndDir(self, dir):
        self._end_dir = dir

    def paint(self, painter: QPainter, option, widget):
        self.prepareGeometryChange()
        self.updatePath()

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
    def updatePath(self):
        self._start_pos = self._start_pin.scene_pos

        if self._end_pin is not None:
            self._end_pos = self._end_pin.scene_pos

        path = QPainterPath(self._start_pos)

        xwidth = self._start_pos.x()-self._end_pos.x()

        xwidth = xwidth+0.01 if xwidth == 0 else xwidth

        yheight = abs(self._start_pos.y()-self._end_pos.y())

        tangent = float(yheight)/xwidth*0.5

        tangent *= xwidth

        if xwidth > 0:
            if xwidth > 150:
                xwidth = 150
            # if self._dir == self.RIGHT:
            #     tangent += xwidth
        else:
            if tangent > 150:
                tangent = 150
            # if self._dir == self.LEFT:
            #     tangent -= xwidth

        start_x = self._start_pos.x()
        start_y = self._start_pos.y()
        end_x = self._end_pos.x()
        end_y = self._end_pos.y()

        if self._dir == self.LEFT:
            start_x -= tangent
        elif self._dir == self.RIGHT:
            start_x += tangent
        elif self._dir == self.UP:
            start_y -= tangent
        elif self._dir == self.DOWN:
            start_y += tangent

        if self._end_dir == self.LEFT:
            end_x -= tangent
        elif self._end_dir == self.RIGHT:
            end_x += tangent
        elif self._end_dir == self.UP:
            end_y -= tangent
        elif self._end_dir == self.DOWN:
            end_y += tangent

        path.cubicTo(QPointF(start_x, start_y),
                     QPointF(end_x, end_y), self._end_pos)

        self.setPath(path)
