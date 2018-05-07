#!/usr/bin/python

import server as gt
import simplefft

import argparse
import logging
import asyncio

defaults = {
    'host': 'localhost',
    'port': 9002,
    "verbose": True
}


def main(args):
    loop = asyncio.get_event_loop()
    server_coro = asyncio.start_server(lambda r,w: gt.handler(r,w,simplefft.process),host=args.host,port= args.port)
    server = loop.run_until_complete(server_coro)
    host = server.sockets[0].getsockname()  # <4>
    print('Serving on {}. Hit CTRL-C to stop.'.format(host))  # <5>
    try:
        loop.run_forever()  # <6>
    except KeyboardInterrupt:  # CTRL+C pressed
        pass
    print('Server shutting down.')
    server.close()  # <7>
    loop.run_until_complete(server.wait_closed())  # <8>
    loop.close()  # <9>


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
