from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PySide6.QtGui import QPen, QBrush, QTransform, QUndoCommand
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtCore import Qt

from widgets.XF_PinWidget import Pin
import uuid
import logging
from abc import abstractmethod


class Device(QGraphicsRectItem):

    MSG_TYPE_LEVEL_TRANSMIT = 0
    MSG_TYPE_LEVEL_REQUEST = 1
    MSG_TYPE_LEVEL_RESPOSE = 2
    MSG_TYPE_DATA_TRANSMIT = 3
    MSG_TYPE_DATA_RECEIVE = 4

    def __init__(self, name, scale=1, svg_path=None):
        super().__init__()
        self.name = name
        self.pins = {}  # 存储所有 Pin
        self.setBrush(QBrush(Qt.transparent))  # 背景颜色
        self.setPen(QPen(Qt.transparent))  # 边框颜色
        self.scale = scale
        self._id = uuid.uuid4().hex
        self._attribute = {"UUID": self._id, "name": name}
        self.scene_pos = None  # 获取当前位置

        # SVG 图像
        self.svg_item = None
        self.is_start = False
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |  # 支持拖动
            QGraphicsRectItem.ItemIsSelectable |  # 支持选中
            QGraphicsRectItem.ItemSendsGeometryChanges  # 更新场景
        )
        if svg_path:
            self.loadSvg(svg_path)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for pin in self.pins.values():
                pin.onMoved()
            self.scene_pos = self.scenePos()
        return super().itemChange(change, value)

    def setVerticalMirror(self):
        transform = QTransform()
        transform.scale(-1, 1)  # 水平镜像
        self.setTransform(transform)
        for pin in self.pins.values():
            pin.setVerticalMirror()

    def setHorizontalMirror(self):
        transform = QTransform()
        transform.scale(1, -1)  # 垂直镜像
        self.setTransform(transform)
        for pin in self.pins.values():
            pin.setHorizontalMirror()

    def setAllMirror(self):
        transform = QTransform()
        transform.scale(-1, -1)  # 水平垂直镜像
        self.setTransform(transform)
        for pin in self.pins.values():
            pin.setAllMirror()

    def setNoMirror(self):
        transform = QTransform()
        transform.scale(1, 1)  # 水平垂直不镜像
        self.setTransform(transform)
        for pin in self.pins.values():
            pin.setNoMirror()

    def setRotation(self, angle):
        if angle % 90 != 0:
            return
        angle = angle % 360
        for i in self.pins.values():
            i.setRota(angle)
        super().setRotation(angle)

    def loadSvg(self, svg_path):
        """加载 SVG 图片"""
        if self.svg_item:
            self.svg_item.setParentItem(None)
            del self.svg_item
        self.svg_item = QGraphicsSvgItem(svg_path)
        self.svg_item.setParentItem(self)  # 将 SVG 图像设置为 Device 的子项
        self.svg_item.setScale(self.scale)  # 根据需要调整比例
        svg_rect = self.svg_item.boundingRect()
        self.width = svg_rect.width() * self.scale
        self.height = svg_rect.height() * self.scale
        self.setRect(0, 0, self.width, self.height)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def addPin(self, pin):
        """添加 Pin 到组件"""
        if isinstance(pin, Pin):
            self.pins[pin.getName()] = pin
            pin.setParentItem(self)  # 将 Pin 添加为组件的子元素
        else:
            raise ValueError("只能添加 Pin 对象")

    def getPinsByType(self, pin_type):
        """根据类型获取 Pins"""
        return [pin for pin in self.pins.values() if pin.pin_type == pin_type]

    def start(self):
        self.is_start = True
        self.setFlags(
            QGraphicsRectItem.ItemIsSelectable |  # 支持选中
            QGraphicsRectItem.ItemSendsGeometryChanges  # 更新场景
        )
        for pin in self.pins.values():
            pin.is_start = True

    def stop(self):
        self.is_start = False
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |  # 支持拖动
            QGraphicsRectItem.ItemIsSelectable |  # 支持选中
            QGraphicsRectItem.ItemSendsGeometryChanges  # 更新场景
        )
        for pin in self.pins.values():
            pin.is_start = False

    def isStart(self):
        return self.is_start

    @property
    def attribute(self) -> dict:
        self._attribute["sence_pos_x"] = self.scene_pos.x()
        self._attribute["sence_pos_y"] = self.scene_pos.y()
        return self._attribute

    @abstractmethod
    def onRunning(self, kwargs: dict = {}):
        """
        用于书写具体处理运行逻辑的函数，该函数会在组件 start() 之后被调用
        先判断 IO 连接是否正确，
        再进行逻辑处理，
        最后通过 sendData 发送数据到输出端
        """
        logging.debug("onRunning")

    def transmitData(self, pin: Pin, type, value):
        if pin.getConnectPins() == []:
            return
        logging.debug(f"{pin.name} transmitData")
        transmit_data = {}
        transmit_data["type"] = type
        transmit_data["value"] = value
        transmit_data["output"] = {}
        transmit_data["output"]["device"] = self
        transmit_data["output"]["pin"] = pin
        transmit_data["output"]["device_uuid"] = self._id
        transmit_data["input"] = {}
        for connect_pin in pin.connect_pins:
            transmit_data["input"]["device"] = connect_pin.parent
            transmit_data["input"]["device_uuid"] = connect_pin.parent._id
            transmit_data["input"]["pin"] = connect_pin
            connect_pin.parent.onRunning(transmit_data.copy())

    def dump(self):
        data = {}
        data["x"] = self.attribute["sence_pos_x"]
        data["y"] = self.attribute["sence_pos_y"]
        data["uuid"] = self.attribute["UUID"]
        return data

    def getID(self):
        return self._id

    @classmethod
    def load(cls, scene, data, is_same_id=True):
        dev = cls()
        scene.addItem(dev)
        dev.setPos(data["x"], data["y"])
        if is_same_id:
            dev._id = data["uuid"]
            dev.attribute["UUID"] = data["uuid"]
        return dev

    def remove(self):
        if self.is_start:
            return None
        return DeviceRemove(self, f"{self.name} remove")


class DeviceRemove(QUndoCommand):
    def __init__(self, device: Device, description="Device Rmove"):
        super().__init__(description)
        self.device = device
        self.cmds = []
        self.scene = self.device.scene()
        logging.info(f"device remove:{description}")
        self.init = True
        for pin in self.device.pins.values():
            for line in pin.getConnectLines():
                cmd = line.remove()
                if cmd is None:
                    continue
                self.cmds.append(cmd)

    def undo(self):
        self.scene.addItem(self.device)
        for cmd in self.cmds:
            cmd.undo()

    def redo(self):
        for cmd in self.cmds:
            cmd.redo()
        self.scene.removeItem(self.device)
