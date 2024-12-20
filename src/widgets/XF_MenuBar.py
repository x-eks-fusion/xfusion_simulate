from PySide6.QtWidgets import QWidget, QApplication, QMenu
from PySide6.QtGui import QAction, QKeySequence, QDesktopServices
from PySide6.QtCore import QUrl

"""
菜单栏
"""


class MenuBar():
    def __init__(self, parent: QWidget | None = ...) -> None:
        self.parent = parent
        self.menu = self.parent.menuBar()
        self.createActions()

        fileMenu = self.menu.addMenu('&文件')
        fileMenu.addAction(self.newGraphAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.saveAllAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)

        self.recent_menu: QMenu = fileMenu.addMenu(
            QApplication.translate("MainWindow", '打开最近图像'))
        self.recent_menu.aboutToShow.connect(self.showRecentFiles)

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
        viewMenu.addAction(self.showRightSidebarAction)

        runMenu = self.menu.addMenu('&执行')
        runMenu.addAction(self.runAction)

        helpMenu = self.menu.addMenu('&帮助')
        helpMenu.addAction(self.gotoCoralAction)
        helpMenu.addAction(self.gotoXFusionDocsAction)

        # 最近文件列表,只记录文件绝对路径
        self.recent_files = []

    def createActions(self):
        self.newGraphAction = QAction(
            QApplication.translate("MainWindow", '新图像'), self.parent)
        self.newGraphAction.setShortcut(QKeySequence.New)

        self.openAction = QAction(QApplication.translate(
            "MainWindow", '打开'), self.parent)
        self.openAction.setShortcut(QKeySequence('Ctrl+O'))

        self.saveAction = QAction(QApplication.translate(
            "MainWindow", '保存'), self.parent)
        self.saveAction.setShortcut(QKeySequence('Ctrl+S'))

        self.saveAsAction = QAction(
            QApplication.translate("MainWindow", '另存为'), self.parent)
        self.saveAsAction.setShortcut(QKeySequence('Ctrl+Shift+S'))

        self.saveAllAction = QAction(
            QApplication.translate("MainWindow", '保存所有'), self.parent)
        self.saveAllAction.setShortcut(QKeySequence('Ctrl+Alt+S'))

        self.quitAction = QAction(QApplication.translate(
            "MainWindow", '退出'), self.parent)
        self.quitAction.setShortcut(QKeySequence('Alt+F4'))

        self.clearMenuAction = QAction(
            QApplication.translate("MainWindow", '清除最近图表'))

        self.copyAction = QAction(QApplication.translate(
            "MainWindow", '复制'), self.parent)
        self.copyAction.setShortcut(QKeySequence('Ctrl+C'))

        self.cutAction = QAction(QApplication.translate(
            "MainWindow", '剪切'), self.parent)
        self.cutAction.setShortcut(QKeySequence('Ctrl+X'))

        self.pasteAction = QAction(
            QApplication.translate("MainWindow", '粘贴'), self.parent)
        self.pasteAction.setShortcut(QKeySequence('Ctrl+V'))

        self.undoAction = QAction(QApplication.translate(
            "MainWindow", '撤销'), self.parent)
        self.undoAction.setShortcut(QKeySequence('Ctrl+Z'))

        self.redoAction = QAction(QApplication.translate(
            "MainWindow", '恢复'), self.parent)
        self.redoAction.setShortcut(QKeySequence('Ctrl+Y'))

        self.delAction = QAction(QApplication.translate(
            "MainWindow", '删除所选'), self.parent)
        self.delAction.setShortcuts(
            [QKeySequence('X'), QKeySequence('Delete')])

        # 全选和全不选
        self.selectAllAction = QAction(
            QApplication.translate("MainWindow", '全选'), self.parent)
        self.selectAllAction.setShortcut(QKeySequence('Ctrl+A'))

        # 全选和全不选
        self.deselectAllAction = QAction(
            QApplication.translate("MainWindow", '取消全选'), self.parent)
        self.deselectAllAction.setShortcut(QKeySequence('Ctrl+D'))

        self.showRightSidebarAction = QAction(
            QApplication.translate("MainWindow", '展示右侧栏'), self.parent)
        self.showRightSidebarAction.setShortcut(QKeySequence('Alt+Shift+R'))
        self.showRightSidebarAction.setCheckable(True)
        self.showRightSidebarAction.setChecked(True)

        # Align Action
        self.alignVCenterAction = QAction(
            QApplication.translate("MainWindow", '垂直居中对齐'), self.parent)
        self.alignVCenterAction.setShortcut(QKeySequence('V'))

        self.verticalDistributedAction = QAction(
            QApplication.translate("MainWindow", '垂直均匀分布'), self.parent)
        self.verticalDistributedAction.setShortcut(QKeySequence('Shift+V'))

        self.alignHCenterAction = QAction(
            QApplication.translate("MainWindow", '水平居中对齐'), self.parent)
        self.alignHCenterAction.setShortcut(QKeySequence('H'))

        self.horizontalDistributedAction = QAction(
            QApplication.translate("MainWindow", '垂直均匀分布'), self.parent)
        self.horizontalDistributedAction.setShortcut(QKeySequence('Shift+H'))

        self.alignLeftAction = QAction(
            QApplication.translate("MainWindow", '水平左对齐'), self.parent)
        self.alignLeftAction.setShortcut(QKeySequence('Shift+L'))

        self.alignRightAction = QAction(
            QApplication.translate("MainWindow", '水平右对齐'), self.parent)
        self.alignRightAction.setShortcut(QKeySequence('Shift+R'))

        self.alignTopAction = QAction(
            QApplication.translate("MainWindow", '垂直顶对齐'), self.parent)
        self.alignTopAction.setShortcut(QKeySequence('Shift+T'))

        self.alignBottomAction = QAction(
            QApplication.translate("MainWindow", '垂直底对齐'), self.parent)
        self.alignBottomAction.setShortcut(QKeySequence('Shift+B'))

        self.straightenEdgeAction = QAction(
            QApplication.translate("MainWindow", '拉直边缘'), self.parent)
        self.straightenEdgeAction.setShortcut(QKeySequence('Q'))

        self.runAction = QAction(QApplication.translate(
            "MainWindow", '运行'), self.parent)
        self.runAction.setShortcut(QKeySequence('Ctrl+R'))

        self.stopAction = QAction(QApplication.translate(
            "MainWindow", '停止'), self.parent)
        self.stopAction.setShortcut(QKeySequence('Ctrl+Shift+R'))

        self.gotoCoralAction = QAction(
            QApplication.translate("MainWindow", '跳转到 Coral 社区'), self.parent)
        self.gotoCoralAction.triggered.connect(self.gotoCoral)
        self.gotoXFusionDocsAction = QAction(
            QApplication.translate("MainWindow", '跳转到 XFusion 文档'), self.parent)
        self.gotoXFusionDocsAction.triggered.connect(self.gotoXFusionDocs)

    def gotoCoral(self):
        QDesktopServices.openUrl(QUrl("https://coral-zone.cc"))

    def gotoXFusionDocs(self):
        QDesktopServices.openUrl(QUrl("https://coral-zone.cc/#/document"))

    def showRecentFiles(self):

        self.recent_menu.clear()

        actions = []
        for filepath in self.recent_files:
            action = QAction(filepath, self)
            # action.triggered.connect(partial(self.load_recent_graph,filepath))
            actions.append(action)

        if len(actions) > 0:
            self.recent_menu.addActions(actions)
        else:
            no_recent = QAction('No recent file.', self.parent)
            no_recent.setDisabled(True)
            self.recent_menu.addAction(no_recent)

        self.recent_menu.addSeparator()
        self.recent_menu.addAction(self.clearMenuAction)
