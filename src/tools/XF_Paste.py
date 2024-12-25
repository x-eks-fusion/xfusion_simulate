from PySide6.QtGui import QUndoCommand
import logging

from tools.XF_Remove import Remove


class Paste(QUndoCommand):
    def __init__(self, window, dx, dy, description="Paste Seleted"):
        super().__init__(description)
        logging.info(f"device paste:{description}")
        self.window = window
        self.clipboard = window.clipboard
        self.editor = window.editor
        self.dx = dx
        self.dy = dy

    def undo(self):
        self.dx = 0
        self.dy = 0
        cmd = Remove(self.seleted_items)
        Remove.redo(cmd)

    def redo(self):
        self.window.deselectAll()
        self.editor.pasteSeletedItem(self.clipboard, self.dx, self.dy)
        self.seleted_items = self.editor.getSelectedItems()
