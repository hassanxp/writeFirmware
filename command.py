import numpy as np


class Command:

    def setCommand(self, name: str):
        self.name = name

    def setBoardId(self, id: np.ushort):
        self.id = id

    def addData(self, data: bytes):
        self.data = data
