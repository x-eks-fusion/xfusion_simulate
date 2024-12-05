from widgets.XF_ItemTreeWidget import ItemTreeWidget

from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QTreeWidgetItem

"""
左上角的函数树控件
"""


class FuncTreeWidget(ItemTreeWidget):

    def setupMenuActions(
            self,
            menu: QMenu,
            item: QTreeWidgetItem,
            action_labels=['New Group', 'New Function', 'Rename', 'Delete']):
        return super().setupMenuActions(menu, item, action_labels)

    def generateName(self, type, default_item_labels=['Group', 'Function']):
        return super().generateName(type, default_item_labels)
