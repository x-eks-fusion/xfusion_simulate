from widgets.XF_ItemTreeWidget import ItemTreeWidget

from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QTreeWidgetItem

"""
左下角的变量树控件
"""


class VariableTreeWidget(ItemTreeWidget):

    def setupMenuActions(self, menu: QMenu, item: QTreeWidgetItem, action_labels=['New Group', 'New Variable', 'Rename', 'Delete']):
        return super().setupMenuActions(menu, item, action_labels)

    def generate_name(self, type, default_item_labels=['Group', 'Variable']):
        return super().generate_name(type, default_item_labels)
