from PySide6.QtWidgets import QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsPathItem
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QFontMetrics
from PySide6.QtCore import QRectF, Qt, QPointF, QPolygonF
from base.XF_Config import Config
from abc import abstractmethod
from enum import Enum


class PortType(Enum):
    NC = 0
    INPUT = 1
    OUTPUT = 2
    INPUT_OUTPUT = 3
    VCC = 4
    GND = 5


class NodePort(QGraphicsItem):
    """
    节点端口基类，连线部分和icon的绘制
    """

    def __init__(self,
                 port_label='',
                 port_color='#ffffff',
                 port_type: PortType = PortType.NC,
                 parent=None,
                 hide_icon=False
                 ):
        """
        :param port_label: 端口名称
        :param port_color: 端口颜色
        :param port_type: 端口类型
        :param parent: 父节点
        :param connected_ports: 连接的端口
        :param hide_icon: 是否隐藏icon
        """
        super().__init__(parent)

        self.config = Config()
        self._port_label = port_label
        self._port_color = port_color
        self._port_type = port_type

        # 定义Pen和Brush
        self._pen_default = QPen(QColor(self._port_color))
        self._pen_default.setWidthF(1.5)
        self._brush_default = QBrush(QColor(self._port_color))
        self._font_size = self.config.EditorConfig["editor_node_pin_label_size"]
        self._port_font = QFont(
            self.config.EditorConfig["editor_node_pin_label_font"], self._font_size)
        self._font_metrics = QFontMetrics(self._port_font)

        self._port_icon_size = self.config.NodeConfig["port_icon_size"]
        self._port_height = self._port_icon_size
        self._port_label_size = self._font_metrics.horizontalAdvance(
            self._port_label)
        self._port_width = self._port_icon_size + self._port_label_size
        self._hide_icon = hide_icon

        # 设置port的值
        self._port_value = None
        self._has_value_set = False

    def boundingRect(self) -> QRectF:
        """定义节点边界矩形，父类的虚函数"""
        return QRectF(0, 0, self._port_width, self._port_icon_size)

    def get_port_pos(self) -> QPointF:
        if self._hide_icon:
            return None
        else:
            self._port_pos = self.scenePos()
            return QPointF(self._port_pos.x() + 0.25 * self._port_icon_size,
                           self._port_pos.y() + 0.5 * self._port_icon_size)


class InputPort(NodePort):
    def __init__(self,
                 port_label='',
                 port_color='#ffffff',
                 parent=None):
        port_type: PortType = PortType.INPUT
        super().__init__(port_label, port_color, port_type, parent, False)

    def paint(self, painter: QPainter, option, widget) -> None:

        port_outline = QPainterPath()
        poly = QPolygonF()
        poly.append(QPointF(0, 0.2*self._port_icon_size))
        poly.append(QPointF(0.25*self._port_icon_size,
                    0.2*self._port_icon_size))
        poly.append(QPointF(self._port_icon_size *
                    0.5, self._port_icon_size*0.5))
        poly.append(QPointF(0.25*self._port_icon_size,
                    0.8*self._port_icon_size))
        poly.append(QPointF(0, 0.8*self._port_icon_size))
        port_outline.addPolygon(poly)

        if not self.is_connected():
            painter.setPen(self._pen_default)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(port_outline.simplified())
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_default)
            painter.drawPath(port_outline.simplified())

        painter.setPen(self._pen_default)
        painter.setFont(self._port_font)
        painter.drawText(QRectF(0.8*self._port_icon_size, 0, self._port_label_size, self._port_icon_size),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         self._port_label)


class OutputPort(NodePort):
    def __init__(self,
                 port_label='',
                 port_color='#ffffff',
                 parent=None):
        port_type: PortType = PortType.OUTPUT
        super().__init__(port_label, port_color, port_type, parent, False)

    def paint(self, painter: QPainter, option, widget) -> None:
        # port label
        painter.setPen(self._pen_default)
        painter.setFont(self._port_font)
        painter.drawText(
            QRectF(0, 0,
                   self._port_label_size, self._port_icon_size),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._port_label)

        # icon o> 来表示
        if not self.is_connected():
            painter.setPen(self._pen_default)
            painter.setBrush(Qt.NoBrush)
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_default)
        painter.drawEllipse(
            QPointF(self._port_label_size+0.5 * self._port_icon_size,
                    0.5 * self._port_icon_size),
            0.25 * self._port_icon_size, 0.25 * self._port_icon_size)
        #  >
        poly = QPolygonF()
        poly.append(
            QPointF(self._port_label_size + 0.85 * self._port_icon_size,
                    0.35 * self._port_icon_size))
        poly.append(
            QPointF(self._port_label_size + 1 * self._port_icon_size,
                    0.5 * self._port_icon_size))
        poly.append(
            QPointF(self._port_label_size + 0.85 * self._port_icon_size,
                    0.65 * self._port_icon_size))

        painter.setBrush(self._brush_default)
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly)


class Pin:
    """
    pin的基类，主要是不同的pin有不同的功能
    """

    def __init__(self,
                 pin_name='',
                 pin_color: QColor = None,
                 pin_widget=None,
                 default_value=None):

        self._pin_name = pin_name
        self._pin_color = pin_color
        self._pin_widget = pin_widget
        self.port = None
        self.default_value = default_value

    @abstractmethod
    def init_port(self, index):
        """
        设置Pin对应的port
        """
        pass

    def get_port(self):
        return self.port


class NCPin(Pin):
    def __init__(self, pin_name, pin_widget=None, default_value=None):
        config = Config()
        pin_color = config.PinConfig["pin_color"]["NC"]
        super().__init__(pin_name, pin_color, pin_widget, default_value)

    def init_port(self, index):
        pass


class InputPin(Pin):
    def __init__(self, pin_name, pin_widget=None, default_value=None):
        config = Config()
        pin_color = config.NodeConfig["pin_color"]["Input"]
        super().__init__(pin_name, pin_color, pin_widget, default_value)

    def init_port(self, index):
        pass


class OutputPin(Pin):
    pass


class InputOutputPin(Pin):
    pass


class VCCPin(Pin):
    pass


class GNDPin(Pin):
    pass


class Node(QGraphicsItem):
    STATE_NORMAL = 0
    STATE_RUNNING = 1
    STATE_FINISHED = 2
    STATE_ERROR = 3

    package_name = ''

    def __init__(self, title, node_color, inputs=[], outputs=[], parent=None, connected_nodes=[]):
        super().__init__(parent)

        self.config = Config()
        self.title = title
        self.node_color = node_color  # 节点颜色
        self.inputs = inputs          # 输入引脚
        self.outputs = outputs        # 输出引脚
        self.state = self.STATE_NORMAL  # 默认状态
        self.connected_nodes = connected_nodes  # 连接的节点

        # 节点尺寸
        self._node_width = 150
        self._node_height = 100
        self._title_height = 30
        self._node_radius = 10  # 圆角半径
        self._socket_spacing = 20

        # 设置阴影效果
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(15)
        self._shadow.setOffset(0, 0)
        self._shadow.setColor(QColor("#00000000"))  # 默认无阴影
        self.setGraphicsEffect(self._shadow)

        # 状态颜色
        self._run_shadow_color = QColor(0, 255, 0, 100)  # 运行中
        self._finished_shadow_color = QColor(0, 0, 255, 100)  # 完成
        self._error_shadow_color = QColor(255, 0, 0, 100)  # 错误
        self._shadow_color = QColor(255, 255, 0, 100)  # 选中状态

        self.setFlags(
            QGraphicsItem.ItemIsMovable |  # 支持拖动
            QGraphicsItem.ItemIsSelectable |  # 支持选中
            QGraphicsItem.ItemSendsGeometryChanges  # 更新场景
        )

        self.init_node_color()

    def itemChange(self, change, value):
        """监控节点状态变化，TODO: 碰撞检测"""
        return super().itemChange(change, value)

    def init_node_color(self):
        """初始化节点颜色"""
        # 选中状态
        self._pen_selected = QPen(QColor('#ddffee00'))
        #  node的背景
        self._brush_background = QBrush(QColor('#dd151515'))

        # color = self.get_title_color()
        self._title_bak_color = self.get_title_color()
        title_color = QColor(self._title_bak_color)
        self._pen_default = QPen(title_color)
        title_color.setAlpha(175)
        self._brush_title_back = QBrush(title_color)

    def get_title_color(self) -> str:
        return self.config.NodeConfig["node_title_back_color"].get(self.package_name,
                                                                   '#4e90fe')

    def boundingRect(self) -> QRectF:
        """定义节点边界矩形，父类的虚函数"""
        return QRectF(0, 0, self._node_width, self._node_height)

    def paint(self, painter: QPainter, option, widget=None):
        """绘制节点"""

        # 阴影效果根据状态变化
        if self.state == self.STATE_NORMAL:
            self._shadow.setColor("#00000000")
        elif self.state == self.STATE_RUNNING:
            self._shadow.setColor(self._run_shadow_color)
        elif self.state == self.STATE_FINISHED:
            self._shadow.setColor(self._finished_shadow_color)
        elif self.state == self.STATE_ERROR:
            self._shadow.setColor(self._error_shadow_color)

        if self.isSelected():
            self._shadow.setColor(self._shadow_color)

        # 1. 绘制节点背景
        node_outline = QPainterPath()
        node_outline.addRoundedRect(
            0, 0, self._node_width, self._node_height, self._node_radius, self._node_radius
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(node_outline.simplified())

        # 2. 绘制标题背景
        title_outline = QPainterPath()
        title_outline.setFillRule(Qt.WindingFill)
        title_outline.addRoundedRect(
            0, 0, self._node_width, self._title_height, self._node_radius, self._node_radius
        )
        # 处理标题区域的下半部分
        title_outline.addRect(0, self._title_height - self._node_radius,
                              self._node_radius, self._node_radius)
        title_outline.addRect(self._node_width - self._node_radius,
                              self._title_height - self._node_radius,
                              self._node_radius, self._node_radius)
        painter.setBrush(self._brush_title_back)
        painter.drawPath(title_outline.simplified())

        # 3. 绘制边框
        if not self.isSelected():
            painter.setPen(self._pen_default)
        else:
            painter.setPen(self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(node_outline)

        # 4. 绘制标题文本
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(Qt.white)
        painter.drawText(
            QRectF(10, 0, self._node_width - 20, self._title_height),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.title,
        )

        # 5. 绘制引脚（输入和输出）
        y_offset = self._title_height + 10
        painter.setBrush(QBrush(Qt.green))
        for i, input_name in enumerate(self.inputs):
            y = y_offset + i * self._socket_spacing
            painter.drawEllipse(-5, y, 10, 10)
            painter.drawText(10, y + 8, input_name)

        painter.setBrush(QBrush(Qt.red))
        for i, output_name in enumerate(self.outputs):
            y = y_offset + i * self._socket_spacing
            painter.drawEllipse(self._node_width - 5, y, 10, 10)
            painter.drawText(self._node_width - 70, y + 8, output_name)
