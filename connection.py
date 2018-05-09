

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
        self.is_exhausted = False
        self.handlers = {
            constants.GADGET_MESSAGE_CONFIG_FILE: self.read_gadget_message_config_file,
            constants.GADGET_MESSAGE_CONFIG_SCRIPT: self.read_gadget_message_config_script,
            constants.GADGET_MESSAGE_PARAMETER_SCRIPT: self.read_gadget_message_parameter_script,
            constants.GADGET_MESSAGE_CLOSE: self.read_gadget_message_close,
            constants.GADGET_MESSAGE_ISMRMRD_ACQUISITION: self.read_gadget_message_ismrmrd_acquisition,
            constants.GADGET_MESSAGE_ISMRMRD_WAVEFORM: self.read_gadget_message_ismrmrd_waveform,
            constants.GADGET_MESSAGE_ISMRMRD_IMAGE: self.read_gadget_message_ismrmrd_image
        }

    def __iter__(self):
        while not self.is_exhausted:
            yield self.next()

    def __next__(self):
        return self.next()

    def read(self, nbytes):
        return self.socket.recv(nbytes, socket.MSG_WAITALL)

    def send_image(self, image):
        self.socket.send(constants.GadgetMessageIdentifier.pack(constants.GADGET_MESSAGE_ISMRMRD_IMAGE))
        self.socket.send(image.getHead())
        self.socket.send(constants.GadgetMessageAttribLength.pack(0))
        self.socket.send(image.data.tobytes())

    def send_acquisition(self, acquisition):
        self.socket.send(constants.GadgetMessageIdentifier.pack(constants.GADGET_MESSAGE_ISMRMRD_ACQUISITION))
        self.socket.send(acquisition.getHead())
        self.socket.send(acquisition.traj.tobytes())
        self.socket.send(acquisition.data.tobytes())

    def send_waveform(self, waveform):
        self.socket.send(constants.GadgetMessageIdentifier.pack(constants.GADGET_MESSAGE_ISMRMRD_WAVEFORM))
        self.socket.send(waveform.getHead())
        self.socket.send(waveform.data.tobytes())

    def next(self):

        id = self.read_gadget_message_identifier()
        handler = self.handlers.get(id, lambda: Connection.unknown_message_identifier(id))

        return handler()

    @staticmethod
    def unknown_message_identifier(identifier):
        logging.error("Received unknown message type: %d", identifier)
        raise StopIteration

    def read_gadget_message_identifier(self):
        identifier_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_IDENTIFIER)
        return constants.GadgetMessageIdentifier.unpack(identifier_bytes)[0]

    def read_gadget_message_length(self):
        length_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_LENGTH)
        return constants.GadgetMessageLength.unpack(length_bytes)[0]

    def read_gadget_message_config_file(self):
        config_file_bytes = self.read(constants.SIZEOF_GADGET_MESSAGE_CONFIGURATION_FILE)
        config_file = constants.GadgetMessageConfigurationFile.unpack(config_file_bytes)[0]

        return config_file

    def read_gadget_message_config_script(self):
        length = self.read_gadget_message_length(self)
        return self.read(length)

    def read_gadget_message_parameter_script(self):
        length = self.read_gadget_message_length()
        return self.read(length)

    def read_gadget_message_close(self):
        self.is_exhausted = True
        raise StopIteration

    def read_gadget_message_ismrmrd_acquisition(self):
        header_bytes = self.read(ctypes.sizeof(ismrmrd.AcquisitionHeader))
        acquisition = ismrmrd.Acquisition(header_bytes)

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

    def read_gadget_message_ismrmrd_waveform(self):
        raise Exception("I don't know how to receive a waveform yet. Sorry.")

    def read_gadget_message_ismrmrd_image(self):
        raise Exception("I don't know how to receive an image yet. Sorry")
