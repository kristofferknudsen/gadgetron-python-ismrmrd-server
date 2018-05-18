

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
        image.serialize_into(self.socket.send)

    def send_acquisition(self, acquisition):
        self.socket.send(constants.GadgetMessageIdentifier.pack(constants.GADGET_MESSAGE_ISMRMRD_ACQUISITION))
        acquisition.serialize_into(self.socket.send)

    def send_waveform(self, waveform):
        self.socket.send(constants.GadgetMessageIdentifier.pack(constants.GADGET_MESSAGE_ISMRMRD_WAVEFORM))
        waveform.serialize_into(self.socket.send)

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
        return ismrmrd.Acquisition.deserialize_from(self.read)

    def read_gadget_message_ismrmrd_waveform(self):
        return ismrmrd.Waveform.deserialize_from(self.read)

    def read_gadget_message_ismrmrd_image(self):
        return ismrmrd.Image.deserialize_from(self.read)
