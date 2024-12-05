from typing import Sequence
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QMessageBox
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize
from tools.XF_QssLoader import QSSLoadTool


class ToolBarWidget(QToolBar):

    def __init__(self, parent=None):
        super().__init__("tool_bar", parent)
        self.setIconSize(QSize(24, 24))  # 设置图标大小
        parent.addToolBar(self)
        QSSLoadTool.setStyleSheetFile(self, './src/qss/menuBar.qss')
        self.running = False

    def addAction(self, icon: str, action: QAction) -> None:
        action.setIcon(QIcon(icon))
        return super().addAction(action)

    def addNewAction(self, icon: str, text, callback) -> None:
        action = QAction(QIcon(icon), text, self)
        action.triggered.connect(callback)
        super().addAction(action)

        return action

    def onRun(self):
        play_icon = QIcon("src/svg/play.png")
        pause_icon = QIcon("src/svg/pause.png")
        if self.running:
            self.action_paly.setIcon(play_icon)
            self.running = False
        else:
            self.action_paly.setIcon(pause_icon)
            self.running = True

    def toolBarAction(self):
        self.action_paly = self.addNewAction(
            "src/svg/play.png", "运行", self.onRun)
