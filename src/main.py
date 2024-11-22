#coding:utf-8
'''
visual graph的入口

'''

import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from widgets.XF_Window import VisualGraphWindow
from tools.XF_QssLoader import QSSLoadTool,resource_path
from base.XF_Config import Config
import logging
from base.XF_Log import logging_setup

if __name__ == "__main__":

    # 加载config配置
    config = Config()
    config.init("./src/config.json")

    # 初始化日志
    logging_setup(logging.DEBUG)

    app = QApplication([])
    app.setStyle('fusion')

    # 设置qss样式表
    QSSLoadTool.setStyleSheetFile(app,'./src/qss/main.qss')

    try:
        editor = VisualGraphWindow()
        editor.setWindowIcon(QIcon(resource_path('./src/icons/icon.ico'))) 
        editor.show()
    except ValueError as e:
        PrintHelper.printError(e)

    sys.exit(app.exec())
