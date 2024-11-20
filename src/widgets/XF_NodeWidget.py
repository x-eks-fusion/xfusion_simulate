from PySide6.QtWidgets import QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsPathItem
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PySide6.QtCore import QRectF, Qt
from base.XF_Config import Config

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
        self.connected_nodes = connected_nodes # 连接的节点

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
        """定义节点边界矩形"""
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
class Socket(QGraphicsItem):
    def __init__(self, x, y, parent, socket_type="input"):
        super().__init__(parent)
        self.socket_type = socket_type  # "input" 或 "output"
        self.setFlags(QGraphicsItem.ItemIsSelectable)

        # 设置连接点
        self.setPos(x, y)

    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setBrush(QBrush(Qt.green if self.socket_type == "input" else Qt.red))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(self.boundingRect())



class Connection(QGraphicsPathItem):
    def __init__(self, start_socket, end_socket=None):
        super().__init__()
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.setPen(QPen(Qt.white, 2))

    def update_path(self):
        """动态更新连线路径"""
        start_pos = self.start_socket.scenePos()
        end_pos = self.end_socket.scenePos() if self.end_socket else start_pos + Qt.QPointF(100, 0)

        path = QPainterPath(start_pos)
        path.cubicTo(
            start_pos.x() + 50, start_pos.y(),
            end_pos.x() - 50, end_pos.y(),
            end_pos.x(), end_pos.y()
        )
        self.setPath(path)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

    app = QApplication([])

    # 创建场景
    scene = QGraphicsScene()
    scene.setSceneRect(-200, -200, 400, 400)

    # 创建节点
    node1 = Node("ForLoop", QColor(50, 50, 150), inputs=["start", "end"], outputs=["index", "Completed"])
    node2 = Node("Add", QColor(50, 150, 50), inputs=["A", "B"], outputs=["Result"])
    scene.addItem(node1)
    scene.addItem(node2)

    node1.setPos(-100, -50)
    node2.setPos(150, -50)

    # 创建视图
    view = QGraphicsView(scene)
    view.setRenderHints(view.renderHints() | QPainter.Antialiasing)
    view.setWindowTitle("Node Editor Example")
    view.resize(800, 600)
    view.show()

    app.exec()
