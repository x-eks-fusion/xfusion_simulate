import logging
from PySide6.QtGui import QUndoCommand


class CutCommand(QUndoCommand):

    def __init__(self, editor, text=""):
        # 必须初始化父类
        super().__init__(text)

        self.editor = editor
        self.items = self.editor.getSelectedItems()

    def undo(self) -> None:
        for item in self.items:
            self.editor.addNode(item)

    def redo(self):
        for item in self.items:
            logging.info(f"item:{type(item)}")
            try:
                item.scene().removeItem(item)
            except AttributeError:
                pass
