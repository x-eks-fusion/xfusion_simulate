from PySide6.QtWidgets import QWidget, QBoxLayout
from PySide6.QtGui import QMouseEvent, QCursor, QUndoStack, QUndoCommand
from PySide6.QtCore import Qt, QPointF
import logging
import PySide6

from widgets.XF_VisualGraphScene import VisualGraphScene
from widgets.XF_NodeListWidget import NodeListWidget
from widgets.XF_VisualGraphView import VisualGraphView
from tools.XF_Command import CutCommand

import numpy as np


"""
中间的TAB控件，包含一个VisualGraphScene和VisualGraphView
"""


class VisualGraphTab(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setup_editor()
        self.undo_stack = QUndoStack(self)
        self.id = np.random.randint(1, 10000)

    # 设置窗口，只需要初始化view
    def setup_editor(self):
        # 窗口位置以及大小
        self.layout = QBoxLayout(QBoxLayout.LeftToRight, self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 初始化scence
        self.scene = VisualGraphScene(self)
        self.view = VisualGraphView(self.scene)
        self.layout.addWidget(self.view)

    def get_selected_items(self):
        return self.scene.selectedItems()

    def del_items(self):
        command = CutCommand(self, 'del items')
        self.add_action_to_stack('del items', command)

    def add_action_to_stack(self, command_text, command: QUndoCommand):
        self.undo_stack.beginMacro(command_text)
        self.undo_stack.push(command)
        self.undo_stack.endMacro()

    def add_node(self, node):
        self.view.add_graph_node(node, pos=None)
