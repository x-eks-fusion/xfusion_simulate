from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PySide6.QtGui import QPen, QBrush, QTransform
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtCore import Qt

from widgets.XF_PinWidget import Pin
import uuid


class Component(QGraphicsRectItem):

    def __init__(self, x, y, name, scale=1, svg_path=None, parent=None):
        super().__init__(x, y, 1, 1, parent)
        self.name = name
        self.pins = []  # 存储所有 Pin
        self.setBrush(QBrush(Qt.transparent))  # 背景颜色
        self.setPen(QPen(Qt.transparent))  # 边框颜色
        self.scale = scale
        self._id = uuid.uuid4()
        self._attribute = {"UUID": self._id.hex, "name": name}
        self.scene_pos = self.scenePos()  # 获取当前位置

        # SVG 图像
        self.svg_item = None
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |  # 支持拖动
            QGraphicsRectItem.ItemIsSelectable |  # 支持选中
            QGraphicsRectItem.ItemSendsGeometryChanges  # 更新场景

        )
        if svg_path:
            self.loadSvg(svg_path)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        for pin in self.pins:
            pin.onMoved()
        self.scene_pos = self.scenePos()
        return super().itemChange(change, value)

    def setVerticalMirror(self):
        transform = QTransform()
        transform.scale(-1, 1)  # 水平镜像
        self.setTransform(transform)
        for pin in self.pins:
            pin.setVerticalMirror()

    def setHorizontalMirror(self):
        transform = QTransform()
        transform.scale(1, -1)  # 垂直镜像
        self.setTransform(transform)
        for pin in self.pins:
            pin.setHorizontalMirror()

    def setAllMirror(self):
        transform = QTransform()
        transform.scale(-1, -1)  # 水平垂直镜像
        self.setTransform(transform)
        for pin in self.pins:
            pin.setAllMirror()

    def setNoMirror(self):
        transform = QTransform()
        transform.scale(1, 1)  # 水平垂直镜像
        self.setTransform(transform)
        for pin in self.pins:
            pin.setNoMirror()

    def setRotation(self, angle):
        if angle % 90 != 0:
            return
        angle = angle % 360
        for i in self.pins:
            i.setRota(angle)
        super().setRotation(angle)

    def loadSvg(self, svg_path):
        """加载 SVG 图片"""
        self.svg_item = QGraphicsSvgItem(svg_path)
        self.svg_item.setParentItem(self)  # 将 SVG 图像设置为 Component 的子项
        self.svg_item.setScale(self.scale)  # 根据需要调整比例
        svg_rect = self.svg_item.boundingRect()
        self.width = svg_rect.width() * self.scale
        self.height = svg_rect.height() * self.scale
        self.setRect(self.x(), self.y(), self.width, self.height)
        # 设置 QGraphicsSvgItem 的位置与 QGraphicsRectItem 对齐
        self.svg_item.setPos(self.x(), self.y())

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def addPin(self, pin):
        """添加 Pin 到组件"""
        if isinstance(pin, Pin):
            self.pins.append(pin)
            pin.setParentItem(self)  # 将 Pin 添加为组件的子元素
        else:
            raise ValueError("只能添加 Pin 对象")

    def removeAllLines(self):
        for pin in self.pins:
            pin.removeAllLines()

    def getPinsByType(self, pin_type):
        """根据类型获取 Pins"""
        return [pin for pin in self.pins if pin.pin_type == pin_type]

    @property
    def attribute(self) -> dict:
        self._attribute["sence_pos_x"] = self.scene_pos.x()
        self._attribute["sence_pos_y"] = self.scene_pos.y()
        return self._attribute
