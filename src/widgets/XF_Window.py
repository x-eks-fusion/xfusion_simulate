# coding:utf-8
'''
编辑器主体

'''

import os
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QFileDialog
from PySide6.QtWidgets import QTabWidget, QApplication, QSplitter
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, Slot, QPoint
import logging

from widgets.XF_NodeListWidget import NodeListWidget

from widgets.XF_SidebarWidgets import SidebarWidget
from widgets.XF_DetailWidget import DetailWidget
from widgets.XF_VariableTreeWidget import VariableTreeWidget
from widgets.XF_FuncTreeWidget import FuncTreeWidget

from widgets.XF_VisualGraphTab import VisualGraphTab

from widgets.XF_MenuBar import MenuBar

from devices.XF_MCU import MCU
from devices.XF_LED import LED
from devices.XF_Button import Button

from widgets.XF_DeviceWidget import Device
from widgets.XF_ToolBarWidget import ToolBarWidget


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
        self.tool_bar = ToolBarWidget(self)
        self.tool_bar.toolBarAction()

        self.actionTriggered()
        # 编辑器设置，位置在中间，占比例至少80%
        self.setupEditor()

        # 初始化左右侧边栏
        self.sidebarInit()

        # 设置布局的初始大小
        self.setupLayout()

        # 剪贴板
        self.clipboard = QApplication.clipboard()

    def setupEditor(self):
        # Visual Graph的编辑器 TabWidget编辑器
        self.editor: VisualGraphTab = None
        self.tab_count = 0
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.setCentralWidget(self.tabWidget)
        self.addOneTab()
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabWidget.tabCloseRequested.connect(self.tabClose)
        self.opened_graphs = {}

    def sidebarInit(self):
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
                'MCU': MCU,
                'Button': Button
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

    @Slot(QTreeWidgetItem)
    def onVariableAdded(self, item: QTreeWidgetItem):
        pass

    @Slot(str, QTreeWidgetItem)
    def onVariableRenamed(self, preName, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole)
        self.editor.view.renameVariable(preName, data['name'])

    @Slot(QTreeWidgetItem)
    def onVariableRegrouped(self, item):
        data = item.data(0, Qt.UserRole)
        self.editor.view.changeVariableGroup(data['name'], data['group'])

    @Slot(QTreeWidgetItem)
    def onVariableDeleted(self, item):
        name = item.data(0, Qt.UserRole)['name']
        self.editor.view.removeVariable(name)

    @Slot(QTreeWidgetItem)
    def onVariableSelected(self, item):
        name = item.data(0, Qt.UserRole)['name']
        selected_var = self.editor.view.getVariable(name)
        # self.detail_widget.refresh(VariableAttrSet(selected_var))

    ###########################################################
    def actionTriggered(self):
        self.menu_bar.connect(self.menu_bar.newGraphAction, self.addOneTab)
        self.menu_bar.connect(self.menu_bar.openAction, self.dialogOpenGraph)
        self.menu_bar.connect(self.menu_bar.saveAction, self.saveGraph)
        self.menu_bar.connect(self.menu_bar.saveAsAction, self.saveGraphAs)
        self.menu_bar.connect(self.menu_bar.saveAllAction, self.saveAllGraph)
        self.menu_bar.connect(self.menu_bar.quitAction, self.quit)
        self.menu_bar.connect(
            self.menu_bar.clearMenuAction, self.clearRecentFiles)
        self.menu_bar.connect(self.menu_bar.copyAction, self.copyItems)
        self.menu_bar.connect(self.menu_bar.cutAction, self.cutItems)
        self.menu_bar.connect(self.menu_bar.pasteAction, self.pasteItems)
        self.menu_bar.connect(self.menu_bar.undoAction, self.undoEdit)
        self.menu_bar.connect(self.menu_bar.redoAction, self.redoEdit)
        self.menu_bar.connect(self.menu_bar.delAction, self.removeSelected)
        self.menu_bar.connect(
            self.menu_bar.selectAllAction, self.selectAllItems)
        self.menu_bar.connect(
            self.menu_bar.deselectAllAction, self.deselectAllItems)
        self.menu_bar.connect(
            self.menu_bar.showLeftSidebarAction, self.showLeft)
        self.menu_bar.connect(
            self.menu_bar.showRightSidebarAction, self.showRight)
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
        self.menu_bar.connect(self.menu_bar.runAction, self.runGraph)
        self.menu_bar.connect(
            self.menu_bar.runInBackAction, self.runGraphInBack)

    def setupLayout(self):
        # 设置中间splitter
        self.setupCenteralSplitter()

        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(self.center_splitter)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes([0, 1500, 250])
        self.splitter.setHandleWidth(3)
        self.setCentralWidget(self.splitter)

    def setupCenteralSplitter(self):

        self.center_splitter = QSplitter(Qt.Vertical, self)
        self.center_splitter.addWidget(self.tabWidget)
        self.center_splitter.setSizes([800, 200])

    @Slot(int)
    def tabChanged(self, index):
        # 当前不的都关闭之后index返回-1
        if index >= 0:
            self.editor = self.tabWidget.currentWidget()
        self.refreshVariableTree()

    @Slot(int)
    def tabClose(self, index):
        self.tabWidget.removeTab(index)
        self.recordGraphClosed(index)

        self.tab_count -= 1

        if self.tabWidget.count() == 0:
            self.addOneTab()

    def addOneTab(self, filepath=None):
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

    @Slot(list)
    def onAttrShowed(self, attrs):
        self.detail_widget.refresh(attrs)

    # model中的函数拖入
    @Slot(QPoint)
    def onNodeDropped(self, pos):
        # 拖拽的是哪个item，从item里面获得class name
        dragged_item = self.model_tree.getDraggedItem()
        if dragged_item is None:
            logging.warning("拖太快了，我都没看清")
            return
        cls = dragged_item.data(0, Qt.UserRole)
        if cls is not None:
            self.editor.view.addGraphNodeWithClsAtViewPoint(cls, pos)

    # 变量拖入
    @Slot(QPoint, bool)
    def onVariableDropped(self, pos, hasControlPressed):
        pass

    def center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()

        self.center_move = [(screen.width() - size.width()) / 2-200,
                            (screen.height() - size.height()) / 2]
        self.move(self.center_move[0], self.center_move[1])

    # 节点对齐
    @Slot()
    def alignVCenter(self):
        '''垂直中心对齐'''
        pass

    @Slot()
    def alignHCenter(self):
        '''水平中心对齐'''
        pass

    @Slot()
    def alignVDistributed(self):
        pass

    @Slot()
    def alignHDistributed(self):
        pass

    @Slot()
    def alignLeft(self):
        pass

    @Slot()
    def alignRight(self):
        pass

    @Slot()
    def alignTop(self):
        pass

    @Slot()
    def alignBottom(self):
        pass

    @Slot()
    def straightenEdge(self):
        pass

    # 全选和全不选
    @Slot()
    def selectAllItems(self):
        pass

    @Slot()
    def deselectAllItems(self):
        pass

    # ################# Render 操作
    @Slot()
    def renderSelected(self):
        pass

    @Slot()
    def renderGraph(self):
        pass

    @Slot()
    def showLeft(self):
        if self.left_sidebar.isVisibleTo(self):
            self.left_sidebar.hide()
        else:
            self.left_sidebar.show()

    @Slot()
    def showRight(self):
        if self.right_sidebar.isVisibleTo(self):
            self.right_sidebar.hide()
        else:
            self.right_sidebar.show()

    ############### 编辑菜单#####################

    # 将选中的node进行复制
    @Slot()
    def copyItems(self):
        pass

    @Slot()
    def cutItems(self):
        pass

    @Slot()
    def pasteItems(self):
        pass

    @Slot()
    def undoEdit(self):
        pass

    @Slot()
    def redoEdit(self):
        pass

    @Slot()
    def removeSelected(self):
        items = self.editor.getSelectedItems()
        for item in items:
            if not isinstance(item, Device):
                continue
            item.removeAllLines()
        self.editor.delItems()

    @Slot()
    def runGraph(self):
        pass

    @Slot()
    def runGraphInBack(self):
        pass

    ############## 文件操作 #################

    @Slot(str)
    def addToRecentFile(self, filepath):
        pass

    @Slot()
    def clearRecentFiles(self):
        pass

    @Slot()
    def saveAllGraph(self):
        pass

    @Slot()
    def saveGraph(self):
        pass

    def saveGraphInView(self, tabview, index):
        if not tabview.saveGraph_in_current_view():
            filepath, filetype = QFileDialog.getSaveFileName(
                self, '保存为', os.getcwd(), 'Visual Graph File (*.vgf)')

            if filepath == '':
                logging.debug('文件选择已取消')
                return

            self.tabWidget.setTabText(index, os.path.basename(filepath))

            self.addToRecentFile(filepath)
            self.recordGraphOpened(filepath, index)
            tabview.saveGraph_in_current_view_as(filepath)

    # 将当前的graph另存为文件
    @Slot()
    def saveGraphAs(self):

        # 弹出对话框，选择文件夹以及保存文件的名字
        filepath, filetype = QFileDialog.getSaveFileName(
            self, '另存为', os.getcwd(), 'Visual Graph File (*.vgf)')

        if filepath == '':
            logging.debug('文件选择已取消')
            return

        self.tabWidget.setTabText(
            self.tabWidget.currentIndex(), os.path.basename(filepath))

        # 将当前选择的路径，传入要保存的file内
        self.addToRecentFile(filepath)
        self.recordGraphOpened(filepath, self.tabWidget.currentIndex())
        self.editor.saveGraph_in_current_view_as(filepath)

    @Slot()
    def dialogOpenGraph(self):
        # 弹出对话框选择文件
        filepath, filetype = QFileDialog.getOpenFileName(
            self, '选择文件', os.getcwd(), 'Visual Graph File (*.vgf)')

        if filepath == '':
            logging.debug('文件选择已取消')
            return

        self.openGraph(filepath)

    def openGraph(self, filepath):

        self.addToRecentFile(filepath)

        index = self.isGraphOpened(filepath)
        if index != -1:
            self.tabWidget.setCurrentIndex(index)
            return

        # 当前的tab是不是没有存储，如果没有存储，则在当前的tab上进行load
        if self.editor.is_untitled_view():
            # 创建一个新的tab，并将graphload到新的tab中
            self.addOneTab(filepath)
        else:
            self.tabWidget.setTabText(
                self.tabWidget.currentIndex(), os.path.basename(filepath))

        self.recordGraphOpened(filepath, self.tabWidget.currentIndex())
        self.editor.load_graph_to_current_view(filepath)
        self.refreshVariableTree()

    def recordGraphOpened(self, filepath, index):
        self.opened_graphs[filepath] = index

    def recordGraphClosed(self, index):

        for filepath, tab_index in self.opened_graphs.items():
            if tab_index > index:
                self.opened_graphs[filepath] = tab_index-1

            elif tab_index == index:
                self.opened_graphs[filepath] = -1

    def isGraphOpened(self, filepath):
        return self.opened_graphs.get(filepath, -1)

    # 退出
    @Slot()
    def quit(self):
        QApplication.quit()
