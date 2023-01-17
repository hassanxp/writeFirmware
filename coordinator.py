import argparse
import logging

from typing import List
from packetizer import Packetizer
from packet import Packet
from command import Command
from controlboard import ControlBoard
from response import Response
import numpy as np
import threading

logger = logging.getLogger('Coordinator')


class ResponseTimeOutError(Exception):
    """Exception raised when a response to a sent command has timed out.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CommandFailError(Exception):
    """Exception raised when a sent command has failed.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Coordinator:

    def __init__(self, timeout: int = 1, nsteps: int = 1):
        self.timeout = timeout
        self.interval = timeout // nsteps
        self.result_available = threading.Event()

    def getPathForId(self, id: int) -> str:
        return 'some-path-to-firmware'

    def process(self, directory: str, ids: List[int]) -> None:

        packetizer = Packetizer()

        # Compute packets for _all_ controllers before connecting to hardware just
        # in case of errors
        dataMap = dict()

        for id in ids:
            path = self.getPathForId(id)
            packets = packetizer.getPackets(path)
            dataMap[id] = packets

        controlBoard = ControlBoard()  # connect to serial bus
        for id, packets in dataMap.items():
            logger.info(f"Writing firmware for controller {id}.. ")
            self.writePackets(controlBoard, id, packets)

    def handleCommand(self, command, controlBoard):
        controlBoard.send(command)
        thread = threading.Thread(target=controlBoard.recv())
        thread.start()
        while not self.result_available.wait(timeout=self.timeout):
            response = controlBoard.recv()
            if response:
                if response == Response.FAIL:
                    raise CommandFailError(f'Command {command.name} for id {command.id} failed')
                return
            logger.debug(f'No response yet. Wait for {self.interval} seconds')
            thread.sleep(self.interval)

        raise ResponseTimeOutError(f'Command {command.name} for id {command.id} timed out.')

    def writePackets(self, controlBoard, id: np.ushort, packets: List[Packet]) -> None:
        command = Command()

        command.setCommand('WriteFirmware')
        command.setBoardId(id)
        self.handleCommand(command, controlBoard)

        command.setCommand('WriteData')
        nPackets = len(packets)
        for count, packet in enumerate(packets):
            logger.info(f'Writing out packet {count} of {nPackets} packets..')
            command.setBoardId(id)
            command.addData(packet)
            self.handleCommand(command, controlBoard)

        command.setCommand('WriteComplete')
        command.setBoardId(id)
        self.handleCommand(command, controlBoard)


def main() -> None:
    parser = argparse.ArgumentParser(prog='Coordinator',
                                     description='Writes firmware updates')

    parser.add_argument('directory', help='location of firmware update.')
    parser.add_argument('ids', metavar='id', type=int, nargs='+',
                        help='list of controller board identifiers')
    parser.add_argument('-log',
                        '--loglevel',
                        default='INFO',
                        choices=logging._nameToLevel.keys(),
                        help='Provide logging level. Example --loglevel debug, default=info')

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel.upper())
    logging.info('Logging now setup.')

    coordinator = Coordinator()
    coordinator.process(args.directory, args.ids)


if __name__ == "__main__":
    main()
