from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QAction, QKeySequence

"""
菜单栏
"""

class MenuBar():
    def __init__(self, parent: QWidget | None = ...) -> None:
        self.parent = parent
        self.menu = self.parent.menuBar()
        self.create_actions()

        fileMenu = self.menu.addMenu('&文件')
        fileMenu.addAction(self.newGraphAction)
        fileMenu.addAction(self.newEditorAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.workspaceAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.saveAllAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)

        self.recent_menu = fileMenu.addMenu(QApplication.translate("MainWindow", '打开最近图像'))
        self.recent_menu.aboutToShow.connect(self.show_recent_files)

        editMenu = self.menu.addMenu('&编辑')
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(self.delAction)
        editMenu.addSeparator()
        editMenu.addAction(self.commentAction)
        editMenu.addSeparator()
        editMenu.addAction(self.selectAllAction)
        editMenu.addAction(self.deselectAllAction)

        alignMenu = self.menu.addMenu('&对齐')
        alignMenu.addAction(self.alignVCenterAction)
        alignMenu.addAction(self.alignHCenterAction)
        alignMenu.addSeparator()
        alignMenu.addAction(self.verticalDistributedAction)
        alignMenu.addAction(self.horizontalDistributedAction)
        alignMenu.addSeparator()
        alignMenu.addAction(self.alignLeftAction)
        alignMenu.addAction(self.alignRightAction)
        alignMenu.addAction(self.alignTopAction)
        alignMenu.addAction(self.alignBottomAction)
        alignMenu.addSeparator()
        alignMenu.addAction(self.straightenEdgeAction)

        viewMenu = self.menu.addMenu('&视图')
        viewMenu.addAction(self.showLeftSidebarAction)
        viewMenu.addAction(self.showRightSidebarAction)

        renderMenu = self.menu.addMenu('&渲染')
        renderMenu.addAction(self.renderSelectedAction)
        renderMenu.addAction(self.renderAllNodesAction)


        runMenu = self.menu.addMenu('&执行')
        runMenu.addAction(self.runAction)
        runMenu.addAction(self.runInBackAction)

        helpMenu = self.menu.addMenu('&帮助')

        # 最近文件列表,只记录文件绝对路径
        self.recent_files = []


    def create_actions(self):
        self.newGraphAction = QAction(QApplication.translate("MainWindow", '新图像'),self.parent)
        self.newGraphAction.setShortcut(QKeySequence.New)

        self.newEditorAction = QAction(QApplication.translate("MainWindow", '新窗口'), self.parent)
        self.newEditorAction.setShortcut(QKeySequence('Ctrl+Shift+N'))

        self.openAction = QAction(QApplication.translate("MainWindow", '打开'),self.parent)
        self.openAction.setShortcut(QKeySequence('Ctrl+O'))

        self.workspaceAction = QAction(QApplication.translate("MainWindow", '设置工作区路径'), self.parent)


        self.saveAction = QAction(QApplication.translate("MainWindow", '保存'),self.parent)
        self.saveAction.setShortcut(QKeySequence('Ctrl+S'))

        self.saveAsAction = QAction(QApplication.translate("MainWindow", '另存为'), self.parent)
        self.saveAsAction.setShortcut(QKeySequence('Ctrl+Shift+S'))

        self.saveAllAction = QAction(QApplication.translate("MainWindow", '保存所有'), self.parent)
        self.saveAllAction.setShortcut(QKeySequence('Ctrl+Alt+S'))

        self.quitAction = QAction(QApplication.translate("MainWindow", '退出'), self.parent)
        self.quitAction.setShortcut(QKeySequence('Alt+F4'))

        self.clearMenuAction = QAction(QApplication.translate("MainWindow", '清除最近图表'))

        self.copyAction = QAction(QApplication.translate("MainWindow", '复制'),self.parent)
        self.copyAction.setShortcut(QKeySequence('Ctrl+C'))

        self.cutAction = QAction(QApplication.translate("MainWindow", '剪切'), self.parent)
        self.cutAction.setShortcut(QKeySequence('Ctrl+X'))

        self.pasteAction = QAction(QApplication.translate("MainWindow", '粘贴'),self.parent)
        self.pasteAction.setShortcut(QKeySequence('Ctrl+V'))


        self.undoAction = QAction(QApplication.translate("MainWindow", '撤销'),self.parent)
        self.undoAction.setShortcut(QKeySequence('Ctrl+Z'))


        self.redoAction = QAction(QApplication.translate("MainWindow", '恢复'),self.parent)
        self.redoAction.setShortcut(QKeySequence('Ctrl+Y'))

        self.delAction = QAction(QApplication.translate("MainWindow", '删除所选'),self.parent)
        self.delAction.setShortcuts([QKeySequence('X'),QKeySequence('Delete')])


        self.commentAction = QAction(QApplication.translate("MainWindow", '注释节点'),self.parent)
        self.commentAction.setShortcut(QKeySequence('Ctrl+Alt+C'))

        # 全选和全不选
        self.selectAllAction = QAction(QApplication.translate("MainWindow", '全选'),self.parent)
        self.selectAllAction.setShortcut(QKeySequence('Ctrl+A'))


        # 全选和全不选
        self.deselectAllAction = QAction(QApplication.translate("MainWindow", '取消全选'), self.parent)
        self.deselectAllAction.setShortcut(QKeySequence('Ctrl+D'))

        self.showLeftSidebarAction = QAction(QApplication.translate("MainWindow", '展示左侧栏'), self.parent)
        self.showLeftSidebarAction.setShortcut(QKeySequence('Alt+Shift+L'))
        self.showLeftSidebarAction.setCheckable(True)
        self.showLeftSidebarAction.setChecked(True)

        self.showRightSidebarAction = QAction(QApplication.translate("MainWindow", '展示右侧栏'), self.parent)
        self.showRightSidebarAction.setShortcut(QKeySequence('Alt+Shift+R'))
        self.showRightSidebarAction.setCheckable(True)
        self.showRightSidebarAction.setChecked(True)

        # renderAction
        self.renderSelectedAction = QAction(QApplication.translate("MainWindow", '渲染所选节点'),self.parent)
        self.renderSelectedAction.setShortcut(QKeySequence('Ctrl+Alt+R'))

        # renderAction
        self.renderAllNodesAction = QAction(QApplication.translate("MainWindow", '渲染整图'), self.parent)
        self.renderAllNodesAction.setShortcut(QKeySequence('Ctrl+Shift+R'))

        # Align Action
        self.alignVCenterAction = QAction(QApplication.translate("MainWindow", '垂直居中对齐'),self.parent)
        self.alignVCenterAction.setShortcut(QKeySequence('V'))

        self.verticalDistributedAction = QAction(QApplication.translate("MainWindow", '垂直均匀分布'), self.parent)
        self.verticalDistributedAction.setShortcut(QKeySequence('Shift+V'))

        self.alignHCenterAction = QAction(QApplication.translate("MainWindow", '水平居中对齐'),self.parent)
        self.alignHCenterAction.setShortcut(QKeySequence('H'))

        self.horizontalDistributedAction = QAction(QApplication.translate("MainWindow", '垂直均匀分布'), self.parent)
        self.horizontalDistributedAction.setShortcut(QKeySequence('Shift+H'))

        self.alignLeftAction = QAction(QApplication.translate("MainWindow", '水平左对齐'), self.parent)
        self.alignLeftAction.setShortcut(QKeySequence('Shift+L'))

        self.alignRightAction = QAction(QApplication.translate("MainWindow", '水平右对齐'), self.parent)
        self.alignRightAction.setShortcut(QKeySequence('Shift+R'))

        self.alignTopAction = QAction(QApplication.translate("MainWindow", '垂直顶对齐'), self.parent)
        self.alignTopAction.setShortcut(QKeySequence('Shift+T'))

        self.alignBottomAction = QAction(QApplication.translate("MainWindow", '垂直底对齐'), self.parent)
        self.alignBottomAction.setShortcut(QKeySequence('Shift+B'))

        self.straightenEdgeAction = QAction(QApplication.translate("MainWindow", '拉直边缘'),self.parent)
        self.straightenEdgeAction.setShortcut(QKeySequence('Q'))

        self.runAction = QAction(QApplication.translate("MainWindow", '运行'),self.parent)
        self.runAction.setShortcut(QKeySequence('Ctrl+R'))

        self.runInBackAction = QAction(QApplication.translate("MainWindow", '后台运行'), self.parent)
        self.runInBackAction.setShortcut(QKeySequence('Ctrl+B'))

    def show_recent_files(self):

        self.recent_menu.clear()

        actions = []
        for filepath in self.recent_files:
            action = QAction(filepath,self)
            # action.triggered.connect(partial(self.load_recent_graph,filepath))
            actions.append(action)

        if len(actions)>0:
            self.recent_menu.addActions(actions)
        else:
            no_recent = QAction('No recent file.',self)
            no_recent.setDisabled(True)
            self.recent_menu.addAction(no_recent)

        self.recent_menu.addSeparator()
        self.recent_menu.addAction(self.clearMenuAction)


    def connect(self, action: QAction, func):
        action.triggered.connect(func)
            