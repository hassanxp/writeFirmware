import numpy as np


class Packet:
    """Defines header and contents of a data packet
    to send to hardware control board for subsequent writing to individual control boards.
    Note that a 16-bit CRC checksum is generated from the data.

    Raises:
    AssertException
        if the supplied data array is greater than the expected data length.
    """
    address: np.ushort
    length: np.ushort
    crc: np.ushort
    data: bytes

    DATA_LENGTH = 200

    def __init__(self,
                 address: np.ushort,
                 data: bytes):

        assert len(data) <= self.DATA_LENGTH
        self.data = data
        self.address = address
        self.length = len(data)
        self.crc = self.computeCRC(data)

    def computeCRC(self, data: bytes) -> np.ushort:
        # FIXME: implement
        return np.ushort(123)
