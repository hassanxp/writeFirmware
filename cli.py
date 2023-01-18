import argparse
import logging


class CommandLineInterface:

    def getArgs():
        parser = argparse.ArgumentParser(prog='Coordinator',
                                         description='Writes firmware updates')

        parser.add_argument('config', help='firmware update details')
        parser.add_argument('ids', metavar='id', type=int, nargs='+',
                            help='list of controller board identifiers')
        parser.add_argument('-log',
                            '--loglevel',
                            default='INFO',
                            choices=logging._nameToLevel.keys(),
                            help='Provide logging level. Example --loglevel debug, default=info')

        args = parser.parse_args()
        return args
