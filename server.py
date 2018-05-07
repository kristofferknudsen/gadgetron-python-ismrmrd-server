
import constants
from connection import Connection

import socket
import logging
import multiprocessing


async def handler(reader, writer, processor):
    connection = Connection(reader)

    config = await connection.__anext__()
    parameters = await connection.__anext__()
    await processor(connection,config,parameters)

