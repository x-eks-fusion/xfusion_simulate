# coding:utf-8

from functools import partial
import logging
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from PySide6.QtWidgets import QScrollArea, QMenu, QSpacerItem
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt, Signal
from os.path import abspath
from tools.XF_QssLoader import QSSLoadTool

"""
左右侧边栏
"""


class SidebarWidget(QWidget):

    def __init__(self, parent=None, title: str = '', isStretch=False):

        super().__init__(parent)

        self.title = title
        self.isStretch = isStretch

        # 记录comp以及对应的状态
        self.comps = {}

        self.setupUI()

        self.setAttribute(Qt.WA_StyledBackground)
        QSSLoadTool.setStyleSheetFile(self, './src/qss/sidebar.qss')

    def setupUI(self):

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        # title Widget
        self.titleWidget = QWidget(self)
        self.titleWidget.setObjectName('SideBarTitle')
        self.titleLayout = QHBoxLayout(self.titleWidget)
        self.titleLayout.setContentsMargins(20, 0, 20, 0)

        self.titleLabel = QLabel(self.title)
        self.menuBtn = QPushButton('···')

        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addStretch(1)
        self.titleLayout.addWidget(self.menuBtn)

        self.contentWidget: ToolBoxWidget = ToolBoxWidget(
            self, isStretch=self.isStretch)
        self.vlayout.addWidget(self.titleWidget)
        self.vlayout.addWidget(self.contentWidget)
        self.vlayout.setSpacing(0)

        # 设置menu actions
        self.refreshMenu()

    def refreshMenu(self):

        btnMenu = QMenu(self)
        self.menuBtn.setMenu(btnMenu)

        # 添加Action，每一个Action是一个选择
        self.checkComp()

        for k, v in self.comps.items():
            action = QAction(k, self)
            action.setCheckable(True)
            action.setChecked(v[1])
            btnMenu.addAction(action)

            action.triggered.connect(partial(self.toggleComp, v[0]))

    # 检测当前有多少comp，以及每一个comp的可见性

    def checkComp(self):
        for name, [comp, vhint] in self.comps.items():
            #  IsVisible返回的可能是对于我们的可见，需要看对于父类空间的可见性
            self.comps[name] = [comp, comp.isVisibleTo(self)]

    def toggleComp(self, comp):
        if comp.isVisibleTo(self):
            logging.debug('hide')
            comp.hide()
            comp.setExpanded(False)
        else:
            logging.debug('show')
            comp.show()
            comp.setExpanded(True)

    def addComp(self, title, widget, collapsed=True, stretch=10):
        comp = self.contentWidget.addDevice(
            title, widget, collapsed, stretch)
        self.comps[title] = [comp, True]
        logging.debug(f"added menu:{title}")
        self.refreshMenu()


class ToolBoxWidget(QWidget):

    compAdded = Signal(QWidget)

    def __init__(self, parent=None, isStretch=False):
        super().__init__(parent)

        self.isStretch = isStretch

        self.scrollArea = QScrollArea(self)
        self.outlayout = QVBoxLayout(self)
        self.outlayout.addWidget(self.scrollArea)
        self.outlayout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget(self)
        self.vlayout = QVBoxLayout(self.widget)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        # compContainer
        self.container = QWidget(self)
        self.containerLayout = QVBoxLayout(self.container)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setSpacing(0)
        self.container.setObjectName('container')

        self.vlayout.addWidget(self.container)

        self.spacer = QSpacerItem(self.width(), self.height(
        ), QSizePolicy.Maximum, QSizePolicy.Expanding)

        # if self.isStretch:
        #     self.vlayout.addItem(self.spacer)

        self.scrollArea.setWidget(self.widget)
        # 这句话非常重要 要不然会不显示
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置qss name
        self.setObjectName('ToolBox')

        # 记录comps
        self.comps: list[ToolBoxDeviceWidget] = []

        self.compAdded.connect(self.onCompAdded)

    # 添加组件
    def addDevice(self, title, contentWidget, collapsed=True, stretch=10):

        comp = ToolBoxDeviceWidget(
            self, collapsed=collapsed, default_stretch=stretch)
        comp.setupWidget(title, contentWidget)

        self.containerLayout.addWidget(comp)

        comp.collapseSig.connect(self.compCollapsed)

        self.comps.append(comp)

        self.compAdded.emit(comp)

        return comp

    def compCollapsed(self, isCollapsed=False):

        allCollapsed = True

        for comp in self.comps:
            if not comp.hasCollapsed():
                self.containerLayout.setStretchFactor(
                    comp, comp.default_stretch)
                allCollapsed = False
            else:
                self.containerLayout.setStretchFactor(comp, 0)

        if allCollapsed:
            self.containerLayout.addItem(self.spacer)
        else:
            self.containerLayout.removeItem(self.spacer)

    def onCompAdded(self, comp):
        self.compCollapsed()


class ToolBoxDeviceWidget(QWidget):

    collapseSig = Signal(bool)

    def __init__(self, parent=None, collapsed=True, default_stretch=10):
        super().__init__(parent)

        # 两个组件
        self.titleWidget = None
        self.contentWidget = None

        # 两个变量
        self.isCollapsed = collapsed

        self.default_stretch = default_stretch

    # 构建widget
    def setupWidget(self, title, contentWidget: QWidget):

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        # title的widget
        self.titleWidget = QPushButton(self)
        self.titleHLayout = QHBoxLayout(self.titleWidget)
        self.titleHLayout.setContentsMargins(10, 0, 10, 0)
        self.titleWidget.setObjectName('ToolCompTitle')

        self.iconLabel = QLabel(self.titleWidget)
        self.iconLabel.setFixedSize(12, 12)
        self.iconLabel.setObjectName('labelIcon')
        self.titleHLayout.addWidget(self.iconLabel)
        self.titleHLayout.addWidget(QLabel(title, self.titleWidget))
        self.titleHLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.vlayout.addWidget(self.titleWidget)
        self.contentWidget = contentWidget
        self.contentWidget.setObjectName('toolContent')
        self.vlayout.addWidget(self.contentWidget)
        self.vlayout.setSpacing(0)

        if self.isCollapsed:
            self.iconLabel.setPixmap(QPixmap(abspath('./src/icons/branch-closed.png')).scaled(
                self.iconLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.contentWidget.hide()
        else:
            self.iconLabel.setPixmap(
                QPixmap(abspath('./src/icons/branch-open.png')).scaled(
                    self.iconLabel.size(), Qt.KeepAspectRatio,
                    Qt.SmoothTransformation))

            self.contentWidget.show()

        self.titleWidget.clicked.connect(self.onTitleClicked)

    def collapse(self):
        self.contentWidget.hide()
        self.isCollapsed = True
        self.iconLabel.setPixmap(
            QPixmap(abspath('./src/icons/branch-closed.png')).scaled(
                self.iconLabel.size(), Qt.KeepAspectRatio,
                Qt.SmoothTransformation))

        self.collapseSig.emit(True)

    def expand(self):
        self.contentWidget.show()
        self.isCollapsed = False
        self.iconLabel.setPixmap(
            QPixmap(abspath('./src/icons/branch-open.png')).scaled(
                self.iconLabel.size(), Qt.KeepAspectRatio,
                Qt.SmoothTransformation))

        self.collapseSig.emit(False)

    def hasCollapsed(self):
        return self.isCollapsed

    def setExpanded(self, expanded):
        if expanded:
            self.expand()
        else:
            self.collapse()

    def onTitleClicked(self):

        if self.isCollapsed:
            self.expand()
        else:
            self.collapse()
