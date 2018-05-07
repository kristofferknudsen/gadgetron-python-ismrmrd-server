

import constants
import ismrmrd
import ctypes

import logging
import socket
import numpy as np


class Connection:
    """
    This is a docstring. It should be a good one.
    """

    def __init__(self, reader):
        self.reader = reader

        self.handlers = {
            constants.GADGET_MESSAGE_CONFIG_FILE: self.read_gadget_message_config_file,
            constants.GADGET_MESSAGE_CONFIG_SCRIPT: self.read_gadget_message_config_script,
            constants.GADGET_MESSAGE_PARAMETER_SCRIPT: self.read_gadget_message_parameter_script,
            constants.GADGET_MESSAGE_CLOSE: self.read_gadget_message_close,
            constants.GADGET_MESSAGE_ISMRMRD_ACQUISITION: self.read_gadget_message_ismrmrd_acquisition
        }

    def __aiter__(self):
        return self

    async def __anext__(self):

        id = await self.read_gadget_message_identifier()

        handler = self.handlers.get(id, lambda: self.unknown_message_identifier(id))

        return await handler()

    async def read_gadget_message_identifier(self):
        identifier_bytes = await self.reader.read(constants.SIZEOF_GADGET_MESSAGE_IDENTIFIER)
        return constants.GadgetMessageIdentifier.unpack(identifier_bytes)[0]

    async def read_gadget_message_length(self):
        length_bytes = await self.reader.read(constants.SIZEOF_GADGET_MESSAGE_LENGTH)
        return constants.GadgetMessageLength.unpack(length_bytes)[0]

    def unknown_message_identifier(self, id):
        logging.error("Received unknown message type: %d", id)
        raise StopIteration

    async def read_gadget_message_config_file(self):
        config_file_bytes = await self.reader.read(constants.SIZEOF_GADGET_MESSAGE_CONFIGURATION_FILE)
        config_file = constants.GadgetMessageConfigurationFile.unpack(config_file_bytes)[0]

        return config_file

    def read_gadget_message_config_script(self):
        # TODO: This.
        raise Exception("I don't know how to 'config script'.")

    async def read_gadget_message_parameter_script(self):
        length = await self.read_gadget_message_length()
        logging.info("Parameter script length: %d", length)

        return await self.reader.read(length)

    def read_gadget_message_close(self):
        raise StopAsyncIteration

    async def read_gadget_message_ismrmrd_acquisition(self):
        header_bytes = await self.reader.readexactly(ctypes.sizeof(ismrmrd.AcquisitionHeader))
        acquisition = ismrmrd.Acquisition(header_bytes)

        nentries = acquisition.number_of_samples * acquisition.active_channels

        data_bytes = await self.reader.readexactly(nentries * constants.SIZEOF_ISMRMRD_DATA_TYPE)
        trajectory_bytes = await self.reader.readexactly(nentries *
                                     acquisition.trajectory_dimensions *
                                     constants.SIZEOF_ISMRMRD_TRAJECTORY_TYPE)

        data = np.frombuffer(data_bytes, dtype=np.complex64)
        trajectory = np.frombuffer(trajectory_bytes, dtype=np.float32)

        acquisition.data[:] = data.reshape((acquisition.active_channels,
                                            acquisition.number_of_samples))[:]
        acquisition.traj[:] = trajectory.reshape((acquisition.number_of_samples,
                                                  acquisition.trajectory_dimensions))[:]

        return acquisition
