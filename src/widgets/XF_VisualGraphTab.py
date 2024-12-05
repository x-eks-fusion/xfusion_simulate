from PySide6.QtWidgets import QWidget, QBoxLayout
from PySide6.QtGui import QUndoStack, QUndoCommand

from widgets.XF_VisualGraphScene import VisualGraphScene
from widgets.XF_VisualGraphView import VisualGraphView
from tools.XF_Command import CutCommand

import numpy as np


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

    def delItems(self):
        command = CutCommand(self, 'del items')
        self.addActionToStack('del items', command)

    def addActionToStack(self, command_text, command: QUndoCommand):
        self.undo_stack.beginMacro(command_text)
        self.undo_stack.push(command)
        self.undo_stack.endMacro()

    def addNode(self, node):
        self.view.addGraphNode(node, pos=None)
