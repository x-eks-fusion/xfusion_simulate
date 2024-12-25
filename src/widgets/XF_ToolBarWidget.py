from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize, Signal, Qt
from tools.XF_QssLoader import QSSLoadTool


class ToolBarWidget(QToolBar):
    run_sig = Signal(bool)

    def __init__(self, parent=None):
        super().__init__("tool_bar", parent)
        self.setIconSize(QSize(36, 36))  # 设置图标大小
        parent.addToolBar(Qt.LeftToolBarArea, self)
        self.setMovable(False)
        QSSLoadTool.setStyleSheetFile(self, './src/qss/toolBar.qss')
        self.play_icon = QIcon("src/svg/toolbar/play.svg")
        self.pause_icon = QIcon("src/svg/toolbar/pause.svg")
        self.open_icon = QIcon("src/svg/toolbar/open.svg")
        self.save_icon = QIcon("src/svg/toolbar/save.svg")
        self.new_icon = QIcon("src/svg/toolbar/new.svg")
        self.undo_icon = QIcon("src/svg/toolbar/undo.svg")
        self.redo_icon = QIcon("src/svg/toolbar/redo.svg")
        self.toolBarAction()

    def addAction(self, icon: str, action: QAction) -> None:
        action.setIcon(QIcon(icon))
        return super().addAction(action)

    def addNewAction(self, icon: QIcon, text) -> QAction:
        action = QAction(icon, text, self)
        super().addAction(action)

        return action

    def onRun(self, is_running):
        if is_running:
            self.action_paly.setIcon(self.pause_icon)
            self.action_paly.setText("暂停")
            self.run_sig.emit(True)
        else:
            self.action_paly.setIcon(self.play_icon)
            self.action_paly.setText("运行")
            self.run_sig.emit(False)

    def run(self):
        self.action_paly.setChecked(True)
        self.onRun(True)

    def stop(self):
        self.action_paly.setChecked(False)
        self.onRun(False)

    def toolBarAction(self):
        self.action_paly = self.addNewAction(self.play_icon, "运行")
        self.action_paly.triggered.connect(self.onRun)
        self.action_paly.setCheckable(True)
        self.addSeparator()
        self.action_new = self.addNewAction(self.new_icon, "新图像")
        self.action_open = self.addNewAction(self.open_icon, "打开")
        self.action_save = self.addNewAction(self.save_icon, "保存")
        self.addSeparator()
        self.action_undo = self.addNewAction(self.undo_icon, "撤销")
        self.action_redo = self.addNewAction(self.redo_icon, "恢复")
