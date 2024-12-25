from PySide6.QtGui import QUndoCommand
import logging


class Remove(QUndoCommand):
    def __init__(self, items, description="Delete Seleted"):
        super().__init__(description)
        logging.info(f"device remove:{description}")
        self.cmds = []

        for item in items:
            if hasattr(item, "remove"):
                cmd = item.remove()
                if cmd is not None:
                    self.cmds.append(cmd)

    def undo(self):
        for cmd in self.cmds:
            cmd.undo()

    def redo(self):
        for cmd in self.cmds:
            cmd.redo()
