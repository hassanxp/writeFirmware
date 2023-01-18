from packet import Packet
from typing import List
import numpy as np


class Packetizer:

    MAX_PACKET_SIZE = 200  # Maximum packet size [byte]

    def toPackets(self, path: str, startAddress: np.ushort) -> List[Packet]:

        length = self.MAX_PACKET_SIZE
        packets = []
        address = startAddress
        data = self.getContents(path)
        while data.length < length:
            chunk = data[:self.length]
            packet = Packet(address=address, data=chunk)
            address += self.length
            packets.append(packet)
            data = data[self.length:]
        if data:
            packet = Packet(address=address, data=data)

    def getContents(self, path: str) -> bytearray:
        # Write dummy value for now
        return bytearray(range(2000))
