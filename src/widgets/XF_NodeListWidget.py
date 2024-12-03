from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from tools.XF_QssLoader import QSSLoadTool

"""
节点树控件
"""


class NodeListWidget(QTreeWidget):
    def __init__(self, data: dict, parent=None, dragEnabled=False):
        super().__init__(parent)

        self.data = data

        # self.resize(200,300)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

        self.construct_tree()
        QSSLoadTool.setStyleSheetFile(self, './src/qss/tree.qss')

        self.setObjectName('MenuTree')

        self.pos = None

        if dragEnabled:
            self.setDragEnabled(True)
            self.viewport().setAcceptDrops(False)
            self.setDragDropMode(QTreeWidget.DragDrop)
            self.setDropIndicatorShown(True)

            rootItem = self.invisibleRootItem()
            rootItem.setFlags(rootItem.flags() ^ Qt.ItemIsDropEnabled)

    def startDrag(self, supportedActions) -> None:

        self.dragged_item = self.itemAt(self.mapFromGlobal(QCursor.pos()))
        return super().startDrag(supportedActions)

    def getDraggedItem(self):
        return self.dragged_item

    def refresh_tree(self, data):
        self.data = data
        self.construct_tree()

    def construct_tree(self, filter=None):
        self.clear()

        items = []
        for pkg_name in self.data.keys():
            item = QTreeWidgetItem([pkg_name])
            flags = item.flags()
            flags ^= Qt.ItemIsSelectable
            flags ^= Qt.ItemIsDropEnabled
            item.setFlags(flags)
            for node_title in self.data[pkg_name].keys():
                node_item = QTreeWidgetItem([node_title])
                node_item.setData(0, Qt.UserRole,
                                  self.data[pkg_name][node_title])
                node_item.setFlags(node_item.flags() ^ Qt.ItemIsDropEnabled)
                item.addChild(node_item)

            items.append(item)

        self.insertTopLevelItems(0, items)
