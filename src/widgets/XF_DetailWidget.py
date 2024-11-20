import logging
from PySide6.QtWidgets import QTreeWidget, QLabel
from PySide6.QtCore import Qt,Signal
from tools.XF_QssLoader import QSSLoadTool
from tools.XF_Tools import VGAttrSet

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

    def __init__(self, attrSet:VGAttrSet,parent=None):
        super().__init__(parent)

        self.setColumnCount(2)
        self.setHeaderHidden(True)

        self.setObjectName('detailTree')
        QSSLoadTool.setStyleSheetFile(self, './src/qss/detail.qss')
        self.setFocusPolicy(Qt.NoFocus)
        self.setIndentation(10)

        self.attrSet = attrSet

        self.refresh(self.attrSet)


    def refresh(self,attrSet):

        if attrSet is None:
            return

        self.clear()
        for i in range(attrSet.getAttrCount()):
            attr = attrSet.getAttrAt(i)
            item = QTreeWidgetItem()
            self.insertTopLevelItem(i,item)
            # 属性名
            name = attr.getAttrName()
            self.setItemWidget(item, 0, QLabel(name))
            widget =  attr.bindWidget(self.onValueChanged,self)
            self.setItemWidget(item, 1,widget)

    def onValueChanged(self,value,func):
        func(value)
        self.valueChanged.emit()


