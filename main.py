#!/usr/bin/python

import server as gt
import simplefft

import argparse
import logging

defaults = {
    'host': 'localhost',
    'port': 9002
}


def main(args):

    server = gt.Server(args.host, args.port, simplefft.process)
    server.serve()


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)

    parser = argparse.ArgumentParser(description='I should be able to write this.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', '--port', type=int, help='Port')
    parser.add_argument('-H', '--host', type=str, help='Host')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')

    parser.set_defaults(**defaults)

    args = parser.parse_args()

    if args.verbose:
        logging.root.setLevel(logging.DEBUG)

    main(args)
