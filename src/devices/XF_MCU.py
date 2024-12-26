from widgets.XF_DeviceWidget import Device
from widgets.XF_PinWidget import VCCOut, GNDOut, Pin, InputOutputPin
from handlers.XF_BaseHandler import send, recv
from PySide6.QtCore import QTimer, QObject
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtWidgets import QMessageBox


class MCU(Device, QObject):

    def __init__(self):
        super().__init__("MCU", 2, svg_path="src/svg/MCU/MCU.svg")
        super(QObject, self).__init__()

        # 添加引脚
        self.vcc = VCCOut(3, 52, 10, Pin.LEFT, self)       # VCC 引脚
        self.gnd = GNDOut(191, 52, 10, Pin.RIGHT, self)       # GND 引脚
        self.addPin(self.vcc)
        self.addPin(self.gnd)
        self.pin = []
        for i in range(0, 18):
            pin = InputOutputPin(
                f"P{i}", 3, 52+18.7*(i+1), 10, Pin.LEFT, self)
            self.pin.append(pin)
            self.addPin(pin)
        for i in range(18, 36):
            pin = InputOutputPin(
                f"P{i}", 191, 52+18.7*(i-17), 10, Pin.RIGHT, self)
            self.pin.append(pin)
            self.addPin(pin)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSceneChange:
            new_scene = value  # 获取即将添加的场景对象
            if not new_scene:  # 如果目标场景存在
                return super().itemChange(change, value)
            for item in new_scene.items():
                # 检查是否已经有相同类型的项
                if isinstance(item, type(self)):
                    msg_box = QMessageBox()
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setWindowTitle("XFusion")
                    msg_box.setText("每个场景只能添加一个MCU")
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec()
                    return None  # 阻止添加到场景
        return super().itemChange(change, value)

    def start(self):
        super().start()
        self.timer = QTimer(self)
        self.timer.setInterval(1)  # 设置定时器间隔为 1000 毫秒（1 秒）
        self.timer.timeout.connect(self.update)
        self.timer.start()
        self.transmitData(self.gnd, Device.MSG_TYPE_LEVEL_TRANSMIT, b'\x00')
        self.transmitData(self.vcc, Device.MSG_TYPE_LEVEL_TRANSMIT, b'\x01')
        while not send.empty():
            send.get()
        while not recv.empty():
            recv.get()

    def stop(self):
        self.timer.stop()
        return super().stop()

    def onRunning(self, kwargs):
        pin = kwargs["input"]["pin"]
        recv.put({"pin": self.pin.index(pin),
                 "value": kwargs["value"], "type": kwargs["type"]})

    def update(self):
        if send.empty():
            return
        data = send.get(block=False)
        self.transmitData(self.pin[data["pin"]], data["type"], data["value"])
