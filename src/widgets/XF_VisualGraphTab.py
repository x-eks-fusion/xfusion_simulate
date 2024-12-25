from PySide6.QtWidgets import QWidget, QBoxLayout
from PySide6.QtGui import QUndoStack

import logging

from widgets.XF_VisualGraphScene import VisualGraphScene
from widgets.XF_VisualGraphView import VisualGraphView

import numpy as np

from widgets.XF_DeviceWidget import Device
from widgets.XF_LineWidget import LineWidget

import uuid


"""
中间的TAB控件，包含一个VisualGraphScene和VisualGraphView
"""


class VisualGraphTab(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupEditor()
        self.undo_stack = QUndoStack(self)
        self.id = np.random.randint(1, 10000)

    # 设置窗口，只需要初始化view
    def setupEditor(self):
        # 窗口位置以及大小
        self.layout = QBoxLayout(QBoxLayout.LeftToRight, self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 初始化scence
        self.scene = VisualGraphScene(self)
        self.view = VisualGraphView(self.scene)
        self.layout.addWidget(self.view)

    def getSelectedItems(self):
        return self.scene.selectedItems()

    def stringifyItems(self, items):
        data = {}
        for item in items:
            if isinstance(item, Device) or isinstance(item, LineWidget):
                key = type(item).__name__
                if key not in data:
                    data[type(item).__name__] = []
                data[type(item).__name__].append(item.dump())
        if "LineWidget" in data:
            lines = data.pop("LineWidget")
            uuid = []
            for values in data.values():
                for value in values:
                    uuid.append(value["uuid"])
            lines_ = []
            for line in lines:
                if line["start_id"] not in uuid or line["end_id"] not in uuid:
                    continue
                lines_.append(line)
            data["LineWidget"] = lines_
        logging.info(data)
        return data

    def stringifySelectItem(self):
        if len(self.getSelectedItems()) > 0:
            return self.stringifyItems(self.getSelectedItems())
        else:
            return None

    def pasteSeletedItem(self, data, dx, dy):
        if "LineWidget" in data:
            lines = data.pop("LineWidget")
            for values in data.values():
                for value in values:
                    uuid_old = value["uuid"]
                    value["x"] += dx
                    value["y"] += dy
                    value["uuid"] = uuid.uuid4().hex
                    for line in lines:
                        if line["start_id"] == uuid_old:
                            line["start_id"] = value["uuid"]
                        if line["end_id"] == uuid_old:
                            line["end_id"] = value["uuid"]
            data["LineWidget"] = lines
        self.scene.load(data, True)
