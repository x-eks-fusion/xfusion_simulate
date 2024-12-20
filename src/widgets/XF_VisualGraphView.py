from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QPointF, Signal, QEvent
from PySide6.QtGui import QPainter, Qt, QMouseEvent
import PySide6

from widgets.XF_NodeListWidget import NodeListWidget

from widgets.XF_DeviceWidget import Device

import logging

"""
中央视图控件
"""


class VisualGraphView(QGraphicsView):
    nodeDropped = Signal(QPointF)
    variableDropped = Signal(QPointF, bool)
    attributeShowed = Signal(list)

    def __init__(self, scene, parent=None):
        super().__init__(scene)

        self.setScene(scene)
        self.setRenderHints(QPainter.Antialiasing
                            | QPainter.TextAntialiasing
                            | QPainter.SmoothPixmapTransform
                            | QPainter.LosslessImageRendering)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scale
        self._zoom_clamp = [0.2, 2]
        self._zoom_factor = 1.05
        self._view_scale = 1.0
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.scene().selectionChanged.connect(self.onSelectionChanged)

    def paintEvent(self, event):
        # 调用自定义方法
        self.onSelectionChanged()

        # 保持原有绘制逻辑
        super().paintEvent(event)

    def onSelectionChanged(self):
        try:
            selected_items = self.scene().selectedItems()
        except RuntimeError:
            return
        attrs = []
        if selected_items is []:
            return
        for item in selected_items:
            if isinstance(item, Device):
                attrs.append(item.attribute)
        self.attributeShowed.emit(attrs)

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.button() == Qt.MiddleButton:
            logging.debug("移动画布")
            self.middleButtonPressed(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.button() == Qt.MiddleButton:
            self.middleButtonRealeased(event)

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.button() == Qt.MiddleButton:
            self.resetTransform()
            self._view_scale = 1.0

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            zoom_factor = self._zoom_factor
        else:
            zoom_factor = 1 / self._zoom_factor

        self._view_scale *= zoom_factor

        if self._view_scale < self._zoom_clamp[
                0] or self._view_scale > self._zoom_clamp[1]:
            zoom_factor = 1.0
            self._view_scale = self._last_scale

        self._last_scale = self._view_scale

        # 每一次相对于上一次的进行缩放
        self.scale(zoom_factor, zoom_factor)

    # 鼠标中间点击

    def middleButtonPressed(self, event):

        if self.itemAt(event.pos()) is not None:
            return
        else:
            # 创建虚拟的左键松开事件
            release_event = QMouseEvent(QEvent.MouseButtonRelease, event.pos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers())
            super().mouseReleaseEvent(release_event)

            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._drag_mode = True
            # 创建虚拟的左键点击事件
            click_event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                      Qt.LeftButton, Qt.NoButton,
                                      event.modifiers())
            super().mousePressEvent(click_event)

    def middleButtonRealeased(self, event):
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.pos(),
                                    Qt.LeftButton, Qt.NoButton,
                                    event.modifiers())
        super().mouseReleaseEvent(release_event)

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self._drag_mode = False

    # 接受drop
    def dragMoveEvent(self, event) -> None:
        if isinstance(event.source(), NodeListWidget):
            event.acceptProposedAction()
        else:
            return super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        if isinstance(event.source(), NodeListWidget):
            self.nodeDropped.emit(event.pos())

        return super().dropEvent(event)

    def addGraphDevice(self,
                       cls,
                       pos: QPointF):
        scene_pos = self.mapToScene(int(pos.x()), int(pos.y()))
        try:
            x = scene_pos.x()
            y = scene_pos.y()
            devices = cls()
            self.scene().addItem(devices)
            devices.setPos(x, y)
        except ValueError as e:
            logging.error(e)

    def findDevice(self, id):
        for i in self.items():
            if isinstance(i, Device) and i.getID() == id:
                return i
        return None

    def connectPinWithInfo(self, id, connect_info):
        start_dev = self.findDevice(id)
        for key, values in connect_info.items():
            if values == []:
                continue
            start_pin = start_dev.pins[key]
            for value in values:
                end_dev = self.findDevice(value[0])
                end_pin = end_dev.pins[value[1]]
                start_pin.connect(end_pin)
