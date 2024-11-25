# coding:utf-8
'''
编辑器主体

'''

import os
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QFileDialog, QTabWidget, QApplication, QSplitter, QTreeWidgetItem
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt
import logging

from widgets.XF_NodeListWidget import NodeListWidget

from widgets.XF_SidebarWidgets import SidebarWidget
from widgets.XF_DetailWidget import DetailWidget
from widgets.XF_VariableTreeWidget import VariableTreeWidget
from widgets.XF_FuncTreeWidget import FuncTreeWidget

from widgets.XF_VisualGraphTab import VisualGraphTab

from widgets.XF_MenuBar import MenuBar

from components.XF_MCU import MCU
from components.XF_LED import LED


class VisualGraphWindow(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(QApplication.translate("MainWindow", 'xfusion'))
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(screen_size.width()*0.95, screen_size.height()*0.9)
        self.center()
        self.splitter = QSplitter(Qt.Horizontal, self)
        # 初始化菜单栏
        self.menu_bar = MenuBar(self)
        self.action_triggered()
        # 编辑器设置，位置在中间，占比例至少80%
        self.setup_editor()

        # 初始化左右侧边栏
        self.initialize_sidebar()

        # 设置布局的初始大小
        self.setup_layout()

        # 剪贴板
        self.clipboard = QApplication.clipboard()

    def setup_editor(self):
        # Visual Graph的编辑器 TabWidget编辑器
        self.editor: VisualGraphTab = None
        self.tab_count = 0
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.setCentralWidget(self.tabWidget)
        self.add_one_tab()
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.tabWidget.tabCloseRequested.connect(self.tab_close)
        self.opened_graphs = {}

    def initialize_sidebar(self):
        # 左边是一个QFrame
        self.left_sidebar = QWidget(self)
        self.left_layout = QVBoxLayout(self.left_sidebar)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        sw = SidebarWidget(title='', isStretch=False)

        # 添加一个树
        self.func_tree = FuncTreeWidget(sw)
        sw.addComp(QApplication.translate(
            "MainWindow", "函数"), self.func_tree, False, 10)

        self.vari_tree = VariableTreeWidget(sw)
        sw.addComp(QApplication.translate(
            "MainWindow", '变量'), self.vari_tree, False, 20)
        self.initVariableTree()

        self.left_layout.addWidget(sw)

        # 右边侧边栏 一个边栏TitleBar
        self.right_sidebar = QWidget(self)
        self.right_layout = QVBoxLayout(self.right_sidebar)
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        sw = SidebarWidget(title='', isStretch=False)

        # 添加一个树
        self.model_tree = NodeListWidget({
            '模块': {
                'LED': LED,
                'MCU': MCU
            }
        }, self, dragEnabled=True)
        sw.addComp(QApplication.translate("MainWindow", '模块库'),
                   self.model_tree, False, 10)

        self.detail_widget = DetailWidget(self)
        sw.addComp(QApplication.translate("MainWindow", '详情'),
                   self.detail_widget, False, 20)
        self.detail_widget.valueChanged.connect(self.refreshVariableTree)

        self.right_layout.addWidget(sw)

    ######################## 变量树##############################################

    # 刷新变量树，根据当前tab
    def refreshVariableTree(self):
        pass

    def initVariableTree(self):
        self.vari_tree.itemAdded.connect(self.onVariableAdded)
        self.vari_tree.itemRenamed.connect(self.onVariableRenamed)
        self.vari_tree.itemRegrouped.connect(self.onVariableRegrouped)
        self.vari_tree.itemDeleted.connect(self.onVariableDeleted)
        self.vari_tree.itemSelected.connect(self.onVariableSelected)
        self.refreshVariableTree()

    def onVariableAdded(self, item: QTreeWidgetItem):
        pass

    def onVariableRenamed(self, preName, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole)
        self.editor.view.renameVariable(preName, data['name'])

    def onVariableRegrouped(self, item):
        data = item.data(0, Qt.UserRole)
        self.editor.view.changeVariableGroup(data['name'], data['group'])

    def onVariableDeleted(self, item):
        name = item.data(0, Qt.UserRole)['name']
        self.editor.view.removeVariable(name)

    def onVariableSelected(self, item):
        name = item.data(0, Qt.UserRole)['name']
        selected_var = self.editor.view.getVariable(name)
        # self.detail_widget.refresh(VariableAttrSet(selected_var))

    ###########################################################
    def action_triggered(self):
        self.menu_bar.connect(self.menu_bar.newGraphAction, self.add_one_tab)
        self.menu_bar.connect(self.menu_bar.openAction, self.dialog_open_graph)
        self.menu_bar.connect(self.menu_bar.saveAction, self.save_graph)
        self.menu_bar.connect(self.menu_bar.saveAsAction, self.save_graph_as)
        self.menu_bar.connect(self.menu_bar.saveAllAction, self.save_all_graph)
        self.menu_bar.connect(self.menu_bar.quitAction, self.quit)
        self.menu_bar.connect(
            self.menu_bar.clearMenuAction, self.clear_recent_files)
        self.menu_bar.connect(self.menu_bar.copyAction, self.copy_items)
        self.menu_bar.connect(self.menu_bar.cutAction, self.cut_items)
        self.menu_bar.connect(self.menu_bar.pasteAction, self.paste_items)
        self.menu_bar.connect(self.menu_bar.undoAction, self.undo_edit)
        self.menu_bar.connect(self.menu_bar.redoAction, self.redo_edit)
        self.menu_bar.connect(self.menu_bar.delAction, self.remove_selected)
        self.menu_bar.connect(
            self.menu_bar.selectAllAction, self.selectAllItems)
        self.menu_bar.connect(
            self.menu_bar.deselectAllAction, self.deselectAllItems)
        self.menu_bar.connect(
            self.menu_bar.showLeftSidebarAction, self.show_left)
        self.menu_bar.connect(
            self.menu_bar.showRightSidebarAction, self.show_right)
        self.menu_bar.connect(
            self.menu_bar.renderSelectedAction, self.renderSelected)
        self.menu_bar.connect(
            self.menu_bar.renderAllNodesAction, self.renderGraph)
        self.menu_bar.connect(
            self.menu_bar.alignVCenterAction, self.alignVCenter)
        self.menu_bar.connect(
            self.menu_bar.verticalDistributedAction, self.alignVDistributed)
        self.menu_bar.connect(
            self.menu_bar.alignHCenterAction, self.alignHCenter)
        self.menu_bar.connect(
            self.menu_bar.horizontalDistributedAction, self.alignHDistributed)
        self.menu_bar.connect(self.menu_bar.alignLeftAction, self.alignLeft)
        self.menu_bar.connect(self.menu_bar.alignRightAction, self.alignRight)
        self.menu_bar.connect(self.menu_bar.alignTopAction, self.alignTop)
        self.menu_bar.connect(
            self.menu_bar.alignBottomAction, self.alignBottom)
        self.menu_bar.connect(
            self.menu_bar.straightenEdgeAction, self.straightenEdge)
        self.menu_bar.connect(self.menu_bar.runAction, self.run_graph)
        self.menu_bar.connect(
            self.menu_bar.runInBackAction, self.run_graph_in_back)

    def setup_layout(self):
        # 设置中间splitter
        self.setup_centeral_splitter()

        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(self.center_splitter)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes([0, 1500, 250])
        self.splitter.setHandleWidth(3)
        self.setCentralWidget(self.splitter)

    def setup_centeral_splitter(self):

        self.center_splitter = QSplitter(Qt.Vertical, self)
        self.center_splitter.addWidget(self.tabWidget)
        self.center_splitter.setSizes([800, 200])

    def tab_changed(self, index):
        # 当前不的都关闭之后index返回-1
        if index >= 0:
            self.editor = self.tabWidget.currentWidget()
        self.refreshVariableTree()

    def tab_close(self, index):
        self.tabWidget.removeTab(index)
        self.record_graph_closed(index)

        self.tab_count -= 1

        if self.tabWidget.count() == 0:
            self.add_one_tab()

    def add_one_tab(self, filepath=None):
        self.tab_count += 1

        tab_view = VisualGraphTab(self)
        if filepath is None or isinstance(filepath, int):
            tab_tile = f'Unititled-{self.tab_count} Graph'
        else:
            tab_tile = os.path.basename(filepath)

        self.tabWidget.addTab(tab_view, tab_tile)
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        self.editor = self.tabWidget.currentWidget()

        tab_view.view.nodeDropped.connect(self.onNodeDropped)
        tab_view.view.variableDropped.connect(self.onVariableDropped)
        tab_view.view.attributeShowed.connect(self.onAttrShowed)

    def onAttrShowed(self, attrs):
        self.detail_widget.refresh(attrs)

    # model中的函数拖入
    def onNodeDropped(self, pos):
        # 拖拽的是哪个item，从item里面获得class name
        dragged_item = self.model_tree.getDraggedItem()
        if dragged_item is None:
            logging.warning("拖太快了，我都没看清")
            return
        cls = dragged_item.data(0, Qt.UserRole)
        if cls is not None:
            self.editor.view.add_graph_node_with_cls_at_view_point(cls, pos)

    # 变量拖入
    def onVariableDropped(self, pos, hasControlPressed):
        pass

    def center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()

        self.center_move = [(screen.width() - size.width()) / 2-200,
                            (screen.height() - size.height()) / 2]
        self.move(self.center_move[0], self.center_move[1])

    # 节点对齐

    def alignVCenter(self):
        '''垂直中心对齐'''
        pass

    def alignHCenter(self):
        '''水平中心对齐'''
        pass

    def alignVDistributed(self):
        pass

    def alignHDistributed(self):
        pass

    def alignLeft(self):
        pass

    def alignRight(self):
        pass

    def alignTop(self):
        pass

    def alignBottom(self):
        pass

    def straightenEdge(self):
        pass

    # 全选和全不选
    def selectAllItems(self):
        pass

    def deselectAllItems(self):
        pass

    # ################# Render 操作
    def renderSelected(self):
        pass

    def renderGraph(self):
        pass

    def show_left(self):
        if self.left_sidebar.isVisibleTo(self):
            self.left_sidebar.hide()
        else:
            self.left_sidebar.show()

    def show_right(self):
        if self.right_sidebar.isVisibleTo(self):
            self.right_sidebar.hide()
        else:
            self.right_sidebar.show()

    ############### 编辑菜单#####################

    # 将选中的node进行复制
    def copy_items(self):
        pass

    def cut_items(self):
        pass

    def paste_items(self):
        pass

    def undo_edit(self):
        pass

    def redo_edit(self):
        pass

    def remove_selected(self):
        self.editor.del_items()

    def run_graph(self):
        pass

    def run_graph_in_back(self):
        pass

    ############## 文件操作 #################

    def add_to_recent_file(self, filepath):
        pass

    def clear_recent_files(self):
        pass

    def save_all_graph(self):
        pass

    def save_graph(self):
        pass

    def save_graph_in_view(self, tabview, index):
        if not tabview.save_graph_in_current_view():
            filepath, filetype = QFileDialog.getSaveFileName(
                self, '保存为', os.getcwd(), 'Visual Graph File (*.vgf)')

            if filepath == '':
                logging.debug('文件选择已取消')
                return

            self.tabWidget.setTabText(index, os.path.basename(filepath))

            self.add_to_recent_file(filepath)
            self.record_graph_opened(filepath, index)
            tabview.save_graph_in_current_view_as(filepath)

    # 将当前的graph另存为文件
    def save_graph_as(self):

        # 弹出对话框，选择文件夹以及保存文件的名字
        filepath, filetype = QFileDialog.getSaveFileName(
            self, '另存为', os.getcwd(), 'Visual Graph File (*.vgf)')

        if filepath == '':
            logging.debug('文件选择已取消')
            return

        self.tabWidget.setTabText(
            self.tabWidget.currentIndex(), os.path.basename(filepath))

        # 将当前选择的路径，传入要保存的file内
        self.add_to_recent_file(filepath)
        self.record_graph_opened(filepath, self.tabWidget.currentIndex())
        self.editor.save_graph_in_current_view_as(filepath)

    def dialog_open_graph(self):
        # 弹出对话框选择文件
        filepath, filetype = QFileDialog.getOpenFileName(
            self, '选择文件', os.getcwd(), 'Visual Graph File (*.vgf)')

        if filepath == '':
            logging.debug('文件选择已取消')
            return

        self.open_graph(filepath)

    def open_graph(self, filepath):

        self.add_to_recent_file(filepath)

        index = self.is_graph_opened(filepath)
        if index != -1:
            self.tabWidget.setCurrentIndex(index)
            return

        # 当前的tab是不是没有存储，如果没有存储，则在当前的tab上进行load
        if self.editor.is_untitled_view():
            # 创建一个新的tab，并将graphload到新的tab中
            self.add_one_tab(filepath)
        else:
            self.tabWidget.setTabText(
                self.tabWidget.currentIndex(), os.path.basename(filepath))

        self.record_graph_opened(filepath, self.tabWidget.currentIndex())
        self.editor.load_graph_to_current_view(filepath)
        self.refreshVariableTree()

    def record_graph_opened(self, filepath, index):
        self.opened_graphs[filepath] = index

    def record_graph_closed(self, index):

        for filepath, tab_index in self.opened_graphs.items():
            if tab_index > index:
                self.opened_graphs[filepath] = tab_index-1

            elif tab_index == index:
                self.opened_graphs[filepath] = -1

    def is_graph_opened(self, filepath):
        return self.opened_graphs.get(filepath, -1)

    # 退出

    def quit(self):
        QApplication.quit()
