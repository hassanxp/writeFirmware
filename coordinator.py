import logging

from typing import List
from typing import Tuple
from packetizer import Packetizer
from packet import Packet
from command import Command
from controlboard import ControlBoard
from response import Response
from cli import CommandLineInterface
import numpy as np
import time
import yaml

logger = logging.getLogger('Coordinator')


class MessagableException(Exception):
    """Write a message with the exception

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ResponseTimeOutError(MessagableException):
    pass


class CommandFailError(MessagableException):
    pass


class InvalidDataException(MessagableException):
    pass


class Coordinator:

    def __init__(self, config, timeout: int = 1, nsteps: int = 1):
        self.timeout = timeout
        self.interval = timeout // nsteps
        self.config = config

    def getInfoForId(self, id: np.ushort) -> Tuple[np.ushort, str]:
        if id not in self.config:
            raise InvalidDataException(f"Controller ID {id} is not in provided config")

        info = self.config[id]
        return (info["address"], info["file"])

    def handleCommand(self, command, controlBoard):
        logger.debug(f'Sending command {command.name} ..')
        elapsedTime = 0
        controlBoard.send(command)
        while not elapsedTime < self.timeout:
            response = controlBoard.recv()
            if response:
                if response == Response.FAIL:
                    raise CommandFailError(f'Command {command.name} for id {command.id} failed')
                logger.debug(f'{command.name} : Response received of {response} ')
                return
            logger.debug(f'No response yet. Wait for {self.interval} seconds')
            time.sleep(self.interval)
            elapsedTime += self.interval
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

    def process(self, directory: str, ids: List[int]) -> None:

        packetizer = Packetizer()

        # Compute packets for _all_ controllers before connecting to hardware just
        # in case of errors
        dataMap = dict()

        for id in ids:
            path, startAddress = self.getInfoForId(directory, id)
            packets = packetizer.getPackets(path, startAddress)
            dataMap[id] = packets

        controlBoard = ControlBoard()  # connect to serial bus
        for id, packets in dataMap.items():
            logger.info(f"Writing firmware for controller {id}.. ")
            self.writePackets(controlBoard, id, packets)


def main() -> None:

    args = CommandLineInterface().getArgs()

    logging.basicConfig(level=args.loglevel.upper())
    logging.info('Logging now setup.')

    with open(args.config, 'r') as f:
        data = yaml.safe_load(f)

    coordinator = Coordinator()
    coordinator.process(args.directory, args.ids, data)


if __name__ == "__main__":
    main()
