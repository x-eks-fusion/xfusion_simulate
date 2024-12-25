# coding:utf-8
'''
编辑器主体

'''

import os
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QFileDialog
from PySide6.QtWidgets import QTabWidget, QApplication, QSplitter
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QGuiApplication, QAction, QCursor
from PySide6.QtCore import Qt, Slot, QPoint

from functools import partial
import logging

from widgets.XF_NodeListWidget import NodeListWidget

from widgets.XF_SidebarWidgets import SidebarWidget
from widgets.XF_DetailWidget import DetailWidget

from widgets.XF_VisualGraphTab import VisualGraphTab

from widgets.XF_MenuBar import MenuBar

from devices.XF_MCU import MCU
from devices.XF_LED import LED
from devices.XF_Button import Button

from widgets.XF_ToolBarWidget import ToolBarWidget
import pickle

from PySide6.QtGui import QUndoStack

from tools.XF_Remove import Remove
from tools.XF_Paste import Paste
from tools.XF_Create import Create


class VisualGraphWindow(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(QApplication.translate("MainWindow", 'XFusion'))
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.size()
        self.resize(screen_size.width()*0.95, screen_size.height()*0.9)
        self.center()

        # 创建撤销堆栈
        self.undo_stack = QUndoStack(self)

        self.splitter = QSplitter(Qt.Horizontal, self)
        # 初始化菜单栏
        self.menu_bar = MenuBar(self)
        self.recent_files = []  # 保存往期的文件
        self.tool_bar = ToolBarWidget(self)

        self.actionTriggered()
        # 初始化右侧边栏
        self.sidebarInit()

        # 编辑器设置，位置在中间，占比例至少80%
        self.setupEditor()

        # 设置布局的初始大小
        self.setupLayout()

        # 剪贴板
        self.clipboard = None
        self.is_run = False

    def show(self):
        super().show()
        self.addOneTab()

    def run(self, is_run):
        if is_run:
            self.is_run = True
            self.editor.view.setDragMode(QGraphicsView.NoDrag)
            self.editor.scene.clearSelection()
            self.model_tree.setDragEnabled(False)
            logging.debug("start")
            for item in self.editor.scene.items():
                if hasattr(item, "start"):
                    item.start()
        else:
            self.is_run = False
            self.editor.view.setDragMode(QGraphicsView.RubberBandDrag)
            self.model_tree.setDragEnabled(True)
            logging.debug("stop")
            for item in self.editor.scene.items():
                if hasattr(item, "stop"):
                    item.stop()

    def setCurrentTabText(self, text):
        self.tabWidget.setTabText(self.tabWidget.currentIndex(), text)

    def getCurrentTabText(self):
        return self.tabWidget.tabText(self.tabWidget.currentIndex())

    def setupEditor(self):
        # Visual Graph的编辑器 TabWidget编辑器
        self.editor: VisualGraphTab = None
        self.tab_count = 0
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabWidget.tabCloseRequested.connect(self.tabClose)
        self.opened_graphs = {}

    def sidebarInit(self):
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

        self.right_layout.addWidget(sw)

    ###########################################################
    def actionTriggered(self):
        self.menu_bar.newGraphAction.triggered.connect(self.addOneTab)
        self.menu_bar.openAction.triggered.connect(self.dialogOpen)
        self.menu_bar.saveAction.triggered.connect(self.saveGraph)
        self.menu_bar.saveAsAction.triggered.connect(self.saveGraphAs)
        self.menu_bar.saveAllAction.triggered.connect(self.saveAllGraph)
        self.menu_bar.recent_menu.aboutToShow.connect(self.showRecentFiles)
        self.menu_bar.clearMenuAction.triggered.connect(self.clearRecentFiles)
        self.menu_bar.quitAction.triggered.connect(self.quit)
        self.menu_bar.delAction.triggered.connect(self.removeSelected)
        self.menu_bar.selectAllAction.triggered.connect(self.selectAll)
        self.menu_bar.deselectAllAction.triggered.connect(self.deselectAll)
        self.menu_bar.undoAction.triggered.connect(self.undo_stack.undo)
        self.menu_bar.redoAction.triggered.connect(self.undo_stack.redo)
        self.menu_bar.showRightSidebarAction.triggered.connect(self.showRight)
        self.menu_bar.copyAction.triggered.connect(self.copy)
        self.menu_bar.pasteAction.triggered.connect(self.paste)
        self.menu_bar.cutAction.triggered.connect(self.cut)
        self.menu_bar.runAction.triggered.connect(self.onRun)
        self.menu_bar.stopAction.triggered.connect(self.onStop)

        self.tool_bar.run_sig.connect(self.run)
        self.tool_bar.action_open.triggered.connect(self.dialogOpen)
        self.tool_bar.action_save.triggered.connect(self.saveGraph)
        self.tool_bar.action_new.triggered.connect(self.addOneTab)
        self.tool_bar.action_undo.triggered.connect(self.undo_stack.undo)
        self.tool_bar.action_redo.triggered.connect(self.undo_stack.redo)

    def onStop(self):
        self.is_run = False
        self.tool_bar.stop()

    def onRun(self):
        self.is_run = True
        self.tool_bar.run()

    def setupLayout(self):
        # 设置中间splitter
        self.setupCenteralSplitter()

        self.splitter.addWidget(self.center_splitter)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes([1500, 250])
        self.splitter.setHandleWidth(2)
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
            cmd = Create(self.editor.view, cls, pos)
            self.undo_stack.push(cmd)

    def center(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()

        self.center_move = [(screen.width() - size.width()) / 2-200,
                            (screen.height() - size.height()) / 2]
        self.move(self.center_move[0], self.center_move[1])

    # ################# Render 操作

    @Slot()
    def showRight(self):
        if self.right_sidebar.isVisibleTo(self):
            self.right_sidebar.hide()
        else:
            self.right_sidebar.show()

    ############### 编辑菜单#####################

    @Slot()
    def removeSelected(self):
        items = self.editor.getSelectedItems()
        cmd = Remove(items)
        self.undo_stack.push(cmd)

    ############## 文件操作 #################

    def addToRecentFile(self, filepath):
        # 最近文件如果存在，则删除后重新插入最前面
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)

        self.recent_files.insert(0, filepath)

        logging.info(f'add file to recent:{self.recent_files}')

    @Slot()
    def saveGraph(self):
        index = self.tabWidget.currentIndex()
        filepath = self.getRecordFilepath(index)
        if filepath is None or not os.path.exists(filepath):
            filepath, filetype = QFileDialog.getSaveFileName(
                self, '保存为', os.getcwd(), 'XFusion Simulation File (*.xfs)')

            if filepath == '':
                logging.debug('文件选择已取消')
                return

            if filepath[-4:] != ".xfs":
                filepath += ".xfs"

            self.tabWidget.setTabText(index, os.path.basename(filepath))

        self.addToRecentFile(filepath)
        self.recordGraphOpened(filepath, self.tabWidget.currentIndex())
        data = self.editor.scene.dump()
        with open(filepath, "wb") as file:
            pickle.dump(data, file)

    # 将当前的graph另存为文件

    @Slot()
    def saveGraphAs(self):
        filepath, filetype = QFileDialog.getSaveFileName(
            self, '另存为', os.getcwd(), 'XFusion Simulation File (*.xfs)')

        if filepath == '':
            logging.debug('文件选择已取消')
            return

        self.tabWidget.setTabText(
            self.tabWidget.currentIndex(), os.path.basename(filepath))

        # 将当前选择的路径，传入要保存的file内
        self.addToRecentFile(filepath)
        self.recordGraphOpened(filepath, self.tabWidget.currentIndex())
        data = self.editor.scene.dump()
        with open(filepath, "wb") as file:
            pickle.dump(data, file)

    @Slot()
    def saveAllGraph(self):
        for index in range(self.tabWidget.count()):
            filepath = self.getRecordFilepath(index)
            if filepath is None or not os.path.exists(filepath):
                filepath, filetype = QFileDialog.getSaveFileName(
                    self, '保存为', os.getcwd(), 'XFusion Simulation File (*.xfs)')

                if filepath == '':
                    logging.debug('文件选择已取消')
                    return

                if filepath[-4:] != ".xfs":
                    filepath += ".xfs"

                self.tabWidget.setTabText(index, os.path.basename(filepath))

            self.addToRecentFile(filepath)
            self.recordGraphOpened(filepath, index)
            data = self.editor.scene.dump()
            with open(filepath, "wb") as file:
                pickle.dump(data, file)

    def loadRecentGraph(self, filepath):
        self.openGraph(filepath)

    @Slot()
    def showRecentFiles(self):

        self.menu_bar.recent_menu.clear()

        actions = []
        for filepath in self.recent_files:
            action = QAction(filepath, self)
            action.triggered.connect(partial(self.loadRecentGraph, filepath))
            actions.append(action)

        if len(actions) > 0:
            self.menu_bar.recent_menu.addActions(actions)
        else:
            no_recent = QAction('没有最近打开的文件', self)
            no_recent.setDisabled(True)
            self.menu_bar.recent_menu.addAction(no_recent)

        self.menu_bar.recent_menu.addSeparator()
        self.menu_bar.recent_menu.addAction(self.menu_bar.clearMenuAction)

    @Slot()
    def clearRecentFiles(self):
        self.recent_files.clear()
        self.showRecentFiles()

    @Slot()
    def dialogOpen(self):
        # 弹出对话框选择文件
        filepath, filetype = QFileDialog.getOpenFileName(
            self, '选择文件', os.getcwd(), 'XFusion Simulation File (*.xfs)')

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
        index = self.tabWidget.currentIndex()
        current_filepath = self.getRecordFilepath(index)
        if current_filepath is not None:
            # 创建一个新的tab，并将graphload到新的tab中
            self.addOneTab(filepath)
        else:
            self.editor.scene.clear()
            self.tabWidget.setTabText(
                self.tabWidget.currentIndex(), os.path.basename(filepath))

        self.recordGraphOpened(filepath, self.tabWidget.currentIndex())
        with open(filepath, "rb") as file:
            data = pickle.load(file)
        self.editor.scene.load(data)

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

    def getRecordFilepath(self, index):
        for filepath, tab_index in self.opened_graphs.items():
            if index == tab_index:
                return filepath
        return None

    # 退出
    @Slot()
    def quit(self):
        QApplication.quit()

    def copy(self):
        selected_items = self.editor.stringifySelectItem()
        if selected_items is None:
            logging.info("nothing selected")
        else:
            self.clipboard = selected_items
            global_pos = QCursor.pos()
            self.clip_pos = self.editor.view.mapToScene(global_pos)

    def paste(self):
        if self.clipboard is None:
            return
        global_pos = QCursor.pos()
        clip_pos = self.editor.view.mapToScene(global_pos)
        dx = clip_pos.x() - self.clip_pos.x()
        dy = clip_pos.y() - self.clip_pos.y()
        cmd = Paste(self, dx, dy)
        self.undo_stack.push(cmd)

    def cut(self):
        self.copy()
        self.removeSelected()

    def selectAll(self):
        for item in self.editor.scene.items():
            item.setSelected(True)

    def deselectAll(self):
        for item in self.editor.scene.items():
            item.setSelected(False)
