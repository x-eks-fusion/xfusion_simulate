from PySide6.QtWidgets import QGraphicsView, QApplication, QTreeWidgetItem
from PySide6.QtCore import QPointF, Signal, QEvent
from PySide6.QtGui import QPainter, Qt, QMouseEvent, QKeyEvent
import PySide6

from widgets.XF_NodeListWidget import NodeListWidget
from widgets.XF_VariableTreeWidget import VariableTreeWidget

import logging

"""
中央视图控件
"""


class VisualGraphView(QGraphicsView):
    nodeDropped = Signal(QPointF)
    variableDropped = Signal(QPointF, bool)

    def __init__(self, scene, parent=None):
        super().__init__(parent)

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
        elif isinstance(event.source(), VariableTreeWidget):
            event.acceptProposedAction()
        else:
            return super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        if isinstance(event.source(), NodeListWidget):
            self.nodeDropped.emit(event.pos())

        if isinstance(event.source(), VariableTreeWidget):
            self.variableDropped.emit(event.pos(),
                                      event.modifiers() == Qt.AltModifier)

        return super().dropEvent(event)

    def add_graph_node(self, node, pos=[0, 0]):
        self.scene().addItem(node)
        if pos is not None:
            node.setPos(pos[0], pos[1])

    def add_graph_node_with_cls(self, cls, pos, centered=False):

        components = cls(pos[0], pos[1])
        if centered:
            pos[0] = pos[0] - components.get_width() / 2

        self.add_graph_node(components, pos)
        return components

    def add_graph_node_with_cls_at_view_point(self,
                                              cls,
                                              pos: QPointF,
                                              centered=True):
        scene_pos = self.mapToScene(int(pos.x()), int(pos.y()))
        try:
            self.add_graph_node_with_cls(
                cls, [scene_pos.x(), scene_pos.y()], centered=centered)
        except ValueError as e:
            logging.error(e)

