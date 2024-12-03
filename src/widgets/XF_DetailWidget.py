from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Signal
from tools.XF_QssLoader import QSSLoadTool

"""
右下角详情信息控件
"""


class DetailWidget(QTreeWidget):

    valueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        QSSLoadTool.setStyleSheetFile(self, './src/qss/detail.qss')
        self.setHeaderHidden(True)
        self.setHeaderLabels(["属性", "值"])

    def refresh(self, attrs):
        self.clear()

        for attr in attrs:
            item = QTreeWidgetItem(self)
            item.setText(0, f"{attr['name']}")
            item.setExpanded(True)
            for key in attr.keys():
                node_item = QTreeWidgetItem(item)
                node_item.setText(0, key)
                node_item.setText(1, f"{attr[key]}")
