from PySide6.QtWidgets import QWidget, QBoxLayout
from PySide6.QtGui import QMouseEvent, QCursor, QUndoStack, QUndoCommand
from PySide6.QtCore import Qt, QPointF
import logging

from widgets.XF_VisualGraphScene import VisualGraphScene
from widgets.XF_NodeListWidget import NodeListWidget
from tools.XF_Tools import PrintHelper
from widgets.XF_VisualGraphView import VisualGraphView

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

    # 聚焦于节点的中心
    def center_graph(self):
        if len(self.view._nodes) > 0:
            pos_x = []
            pos_y = []
            for node in self.view._nodes:

                pos = node.scenePos()
                pos_x.append(pos.x())
                pos_y.append(pos.y())

            self.view.centerOn(QPointF(np.mean(pos_x), np.mean(pos_y)))

    # 将全局鼠标位置映射为场景为止
    def map_mouse_to_scene(self):
        return self.view.mapToScene(
            self.view.mapFromGlobal(QCursor.pos()))

    #################### 编辑操作 ####################
    # 将某个action添加到栈内
    def add_action_to_stack(self, command_text, command: QUndoCommand):
        self.undo_stack.beginMacro(command_text)
        # push的时候会自动的执行一次redo,不需要自己去执行
        self.undo_stack.push(command)
        self.undo_stack.endMacro()

    #  撤销
    def undo_edit(self):
        PrintHelper.debugPrint(
            f'editor {self.id}  undo {self.undo_stack.isActive()}')
        self.undo_stack.undo()
    #  恢复

    def redo_edit(self):
        PrintHelper.debugPrint(f'editor {self.id}  redo')
        self.undo_stack.redo()

    # 将选中的节点转化成json字符串
    def stringfy_selected_items(self):

        if len(self.get_selected_items()) > 0:
            return self.view.stringfy_items(self.get_selected_items())
        else:
            return None

    #  粘贴命令
    def paste_selected_items(self, graph):
        pasteCommand = PasteCommand(self, graph)
        self.add_action_to_stack('Paste Items', pasteCommand)

    # 剪切命令
    def cut_items(self):
        command = CutCommand(self)
        self.add_action_to_stack('cut items', command)

    # 使用剪切命令完成删除
    def del_items(self):
        command = CutCommand(self)
        self.add_action_to_stack('del items', command)

    # 删除selected nodes
    def delete_selected_nodes(self):
        for item in self.get_selected_items():
            if isinstance(item, GraphNode):
                item.remove_self()

    # 获得当前选中的项目
    def get_selected_items(self):
        return self.view.get_selected_items()

    #  deselect 当前选中的项目
    def unselected_selected_items(self):
        return self.view.unselected_selected_items()

    #  选中指定项目
    def select_items(self, items):
        for item in items:
            item.setSelected(True)

    #  将指定项目group
    def group_items(self):
        # 获得选中的nodes
        command = GroupCommand(self)
        self.add_action_to_stack('group items', command)

    #  将指定项目group
    def ungroup_items(self):
        # 获得选中的nodes
        command = UnGroupCommand(self)
        self.add_action_to_stack('ungroup items', command)

    def add_group(self, group):
        self.view.add_node_group_obj(group)

    def remove_group(self, group):
        self.view.delte_node_group(group)

    # ################### 文件操作 ################

    # 判断当前tab是不是未命名
    def is_untitled_view(self):
        return False if self.view.get_saved_path() is None else True

    # 将当前tab进行保存
    def save_graph_in_current_view(self):
        return self.view.save_graph_directly()

    # 将当前tab进行另存为
    def save_graph_in_current_view_as(self, path):
        self.view.save_graph_to_file(path)

    # 将对应路径的graph加载到当前的tab内
    def load_graph_to_current_view(self, path):
        self.view.load_graph(path)
        self.center_graph()

    # 添加节点
    def add_node(self, node):
        self.view.add_graph_node(node, pos=None)

    # 添加边
    def add_edge(self, edge):
        self.view.readd_edge(edge)

    # 运行操作

    def run_graph(self):
        self.view.run_graph()

    def run_graph_in_back(self):
        self.view.run_graph_in_back()

    #  右键点击，添加右键菜单 TODO 将该功能改到window的context menu功能内
    def mousePressEvent(self, event: QMouseEvent) -> None:

        if event.button() == Qt.RightButton and event.modifiers() != Qt.ControlModifier:
            self.show_menu(event.pos())

        super().mousePressEvent(event)

    # def contextMenuEvent(self, event) -> None:
    #     self.show_menu(event.pos())

    # ########## 设置菜单栏

    def setup_menu(self):
        self.refresh_menu_data()
        self._menu_widget = NodeListWidget(self._menu_data, self)
        self._menu_widget.setGeometry(0, 0, 200, 300)
        self.view.setMenuWidget(self._menu_widget)
        self.hide_menu()

        # self._menu_widget.itemDoubleClicked.connect(self.view.node_selected)

    def hide_menu(self):
        self._menu_widget.setVisible(False)

    def show_menu(self, pos):
        self.refresh_menu_data()
        self._menu_widget.refresh_tree(self._menu_data)
        self._menu_widget.setGeometry(pos.x(), pos.y(), 200, 300)
        self._menu_widget.show()

    def refresh_menu_data(self):
        # lib_data = VG_ENV.get_nodelib_json_data()
        # var_data = self.view.getVariableClsData()
        self._menu_data = {}
        # self._menu_data.update(lib_data)
        # self._menu_data.update(var_data)
