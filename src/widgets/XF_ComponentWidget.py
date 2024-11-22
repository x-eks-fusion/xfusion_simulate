from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsColorizeEffect, QStyleOptionGraphicsItem, QWidget
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtCore import Qt
import PySide6
import logging

from widgets.XF_PinWidget import Pin


class Component(QGraphicsRectItem):
    def __init__(self, x, y, name, scale=1, svg_path=None, parent=None):
        super().__init__(x, y, 1, 1, parent)
        self.name = name
        self.pins = []  # 存储所有 Pin
        self.setBrush(QBrush(Qt.transparent))  # 背景颜色
        self.setPen(QPen(Qt.transparent))  # 边框颜色
        self.scale = scale

        # SVG 图像
        self.svg_item = None
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |  # 支持拖动
            QGraphicsRectItem.ItemIsSelectable |  # 支持选中
            QGraphicsRectItem.ItemSendsGeometryChanges  # 更新场景

        )
        if svg_path:
            self.load_svg(svg_path)

    def load_svg(self, svg_path):
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

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def add_pin(self, pin):
        """添加 Pin 到组件"""
        if isinstance(pin, Pin):
            self.pins.append(pin)
            pin.setParentItem(self)  # 将 Pin 添加为组件的子元素
        else:
            raise ValueError("只能添加 Pin 对象")

    def get_pins_by_type(self, pin_type):
        """根据类型获取 Pins"""
        return [pin for pin in self.pins if pin.pin_type == pin_type]

    def remove_self(self):
        self.prepareGeometryChange()
        # TODO 递归删除连接者
        self.scene().removeItem(self)
        self.update()
