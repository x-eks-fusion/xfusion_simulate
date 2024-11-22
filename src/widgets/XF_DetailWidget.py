from PySide6.QtWidgets import QTreeWidget, QLabel, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal
from tools.XF_QssLoader import QSSLoadTool

"""
右下角详情信息控件
"""

'''
[{
    'attr_name':'Name',
    'attr_value': ''
}]

'''


class DetailWidget(QTreeWidget):

    valueChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(2)
        self.setHeaderHidden(True)

        self.setObjectName('detailTree')
        QSSLoadTool.setStyleSheetFile(self, './src/qss/detail.qss')
        self.setFocusPolicy(Qt.NoFocus)
        self.setIndentation(10)

