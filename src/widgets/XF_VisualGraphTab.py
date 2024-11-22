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
        self.setup_menu()
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
        logging.debug(f"scene:{self.view.scene()}")
        logging.debug(f"views:{self.scene.views()}")

    #  右键点击，添加右键菜单 TODO 将该功能改到window的context menu功能内
    def mousePressEvent(self, event: QMouseEvent) -> None:

        if event.button() == Qt.RightButton and event.modifiers() != Qt.ControlModifier:
            self.show_menu(event.pos())

        super().mousePressEvent(event)

    # ########## 设置菜单栏

    def setup_menu(self):
        self.refresh_menu_data()
        self._menu_widget = NodeListWidget(self._menu_data, self)
        self._menu_widget.setGeometry(0, 0, 200, 300)
        self.hide_menu()

    def hide_menu(self):
        self._menu_widget.setVisible(False)

    def show_menu(self, pos):
        self.refresh_menu_data()
        self._menu_widget.refresh_tree(self._menu_data)
        self._menu_widget.setGeometry(pos.x(), pos.y(), 200, 300)
        self._menu_widget.show()

    def refresh_menu_data(self):
        self._menu_data = {
        }

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
