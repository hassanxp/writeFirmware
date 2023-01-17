import unittest
from command import Command
from packet import Packet
import numpy as np


class TestFirmware(unittest.TestCase):

    def test_command(self):
        print('testing..')
        Command()

    def test_packet(self):
        print('testing packets')
        Packet(address=np.ushort(123), data=bytes([1, 2]))


if __name__ == '__main__':
    unittest.main()
