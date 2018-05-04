

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

    def __init__(self, socket):
        self.socket = socket

        self.handlers = {
            constants.GADGET_MESSAGE_CONFIG_FILE: self.read_gadget_message_config_file,
            constants.GADGET_MESSAGE_CONFIG_SCRIPT: self.read_gadget_message_config_script,
            constants.GADGET_MESSAGE_PARAMETER_SCRIPT: self.read_gadget_message_parameter_script,
            constants.GADGET_MESSAGE_CLOSE: self.read_gadget_message_close,
            constants.GADGET_MESSAGE_ISMRMRD_ACQUISITION: self.read_gadget_message_ismrmrd_acquisition
        }

    def __iter__(self):
        return self

    def read(self, nbytes):
        return self.socket.recv(nbytes, socket.MSG_WAITALL)

    def next(self):

        id = self.read_gadget_message_identifier()

        handler = self.handlers.get(id, lambda: self.unknown_message_identifier(id))

        return handler()

    def read_gadget_message_identifier(self):
        identifier_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_IDENTIFIER)
        return constants.GadgetMessageIdentifier.unpack(identifier_bytes)[0]

    def read_gadget_message_length(self):
        length_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_LENGTH)
        return constants.GadgetMessageLength.unpack(length_bytes)[0]

    def unknown_message_identifier(self, id):
        logging.error("Received unknown message type: %d", id)
        raise StopIteration

    def read_gadget_message_config_file(self):
        config_file_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_CONFIGURATION_FILE)
        config_file = constants.GadgetMessageConfigurationFile.unpack(config_file_bytes)[0]

        return config_file

    def read_gadget_message_config_script(self):
        # TODO: This.
        raise Exception("I don't know how to 'config script'.")

    def read_gadget_message_parameter_script(self):
        length = self.read_gadget_message_length()
        logging.info("Parameter script length: %d", length)

        return self.read(length)

    def read_gadget_message_close(self):
        raise StopIteration

    def read_gadget_message_ismrmrd_acquisition(self):
        header_bytes = self.read(ctypes.sizeof(ismrmrd.AcquisitionHeader))
        acquisition = ismrmrd.Acquisition(buffer(header_bytes))

        nentries = acquisition.number_of_samples * acquisition.active_channels

        data_bytes = self.read(nentries * constants.SIZEOF_ISMRMRD_DATA_TYPE)
        trajectory_bytes = self.read(nentries *
                                     acquisition.trajectory_dimensions *
                                     constants.SIZEOF_ISMRMRD_TRAJECTORY_TYPE)

        data = np.frombuffer(data_bytes, dtype=np.complex64)
        trajectory = np.frombuffer(trajectory_bytes, dtype=np.float32)

        acquisition.data[:] = data.reshape((acquisition.active_channels,
                                            acquisition.number_of_samples))[:]
        acquisition.traj[:] = trajectory.reshape((acquisition.number_of_samples,
                                                  acquisition.trajectory_dimensions))[:]

        return acquisition
