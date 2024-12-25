from PySide6.QtGui import QUndoCommand
import logging

from tools.XF_Remove import Remove


class Create(QUndoCommand):
    def __init__(self, view, cls, pos, description="Create Seleted"):
        super().__init__(description)
        logging.info(f"device create:{description}")
        self.view = view
        self.cls = cls
        self.pos = pos
        self.device = None

    def undo(self):
        cmd = Remove([self.device])
        Remove.redo(cmd)

    def redo(self):
        scene_pos = self.view.mapToScene(int(self.pos.x()), int(self.pos.y()))
        try:
            x = scene_pos.x()
            y = scene_pos.y()
            self.device = self.cls()
            self.view.scene().addItem(self.device)
            self.device.setPos(x, y)
        except ValueError as e:
            logging.error(e)
