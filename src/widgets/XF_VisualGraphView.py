from PySide6.QtWidgets import QGraphicsView, QApplication, QTreeWidgetItem
from PySide6.QtCore import QPointF, Signal, QEvent
from PySide6.QtGui import QPainter, Qt, QMouseEvent, QColor
import PySide6
from widgets.XF_NodeWidget import Node

"""
中央视图控件
"""

class VisualGraphView(QGraphicsView):
    nodeDropped = Signal(QPointF)
    variableDropped = Signal(QPointF, bool)
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self._scene = scene

        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing
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

        node1 = Node("ForLoop", QColor(50, 50, 150), inputs=["start", "end"], outputs=["index", "Completed"])
        node2 = Node("Add", QColor(50, 150, 50), inputs=["A", "B"], outputs=["Result"])
        scene.addItem(node1)
        scene.addItem(node2)

        node1.setPos(-100, -50)
        node2.setPos(150, -50)

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.button() == Qt.MiddleButton:
            self.middleButtonPressed(event)
        elif event.button() == Qt.LeftButton:
            self.leftButtonPressed(event)

        elif event.button() == Qt.RightButton:

            self.rightButtonPressed(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

        if event.button() == Qt.MiddleButton:
            self.middleButtonRealeased(event)

        elif event.button() == Qt.LeftButton:
            self.leftButtonReleased(event)

        elif event.button() == Qt.RightButton:

            self.rightButtonReleased(event)

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

    # 鼠标移动事件
    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)

    # 键盘点击
    def keyPressEvent(self, event: PySide6.QtGui.QKeyEvent) -> None:

        return super().keyPressEvent(event)

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

    def leftButtonPressed(self, event: QMouseEvent):
        # 菜单隐藏
        self._menu_widget.hide()

        mouse_pos = event.pos()
        item = self.itemAt(mouse_pos)

        super().mousePressEvent(event)

    def leftButtonReleased(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def rightButtonPressed(self, event):

        item = self.itemAt(event.pos())

        self.setDragMode(QGraphicsView.NoDrag)

        super().mousePressEvent(event)

    def rightButtonReleased(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def setMenuWidget(self, menuW):
        self._menu_widget = menuW

    def node_selected(self, item, column):
        if isinstance(item, QTreeWidgetItem):
            cls = item.data(0, Qt.UserRole)
            if cls is not None:

                geometry = self._menu_widget.geometry()
                pos = QPointF(geometry.x(), geometry.y())
                view_pos = self.mapFromParent(pos)
                scene_pos = self.mapToScene(int(view_pos.x()),
                                            int(view_pos.y()))
                self.add_graph_node_with_cls(
                    cls, [scene_pos.x(), scene_pos.y()])
                self._menu_widget.hide()

    # 接受drop
    def dragMoveEvent(self, event) -> None:
        super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:
        super().dropEvent(event)
        