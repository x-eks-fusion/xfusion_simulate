import logging
from PySide6.QtGui import QUndoCommand


class CutCommand(QUndoCommand):

    def __init__(self, editor, text=""):
        # 必须初始化父类
        super().__init__(text)

        self.editor = editor
        self.items = self.editor.get_selected_items()

    def undo(self) -> None:
        for item in self.items:
            self.editor.add_node(item)

    def redo(self):
        for item in self.items:
            logging.info(f"item:{type(item)}")
            try:
                item.scene().removeItem(item)
            except AttributeError:
                pass
