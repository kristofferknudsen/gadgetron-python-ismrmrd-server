
import ismrmrd

import itertools
import logging
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt


def groups(iterable, predicate):
    group = []
    for item in iterable:
        group.append(item)

        if predicate(item):
            yield group
            group = []


def process(connection, config, params):
    logging.info("Processing connection.")
    logging.info("Config: \n%s", config.decode("utf-8"))
    logging.info("Params: \n%s", params.decode("utf-8"))

    # First group in the simple_gre.h5 dataset inexplicably contains 129 acquisitions.
    # We discard one to preserve the sanity of the gadgetron ismrmrd client (it expects
    # images that are 256x128, not 256x129).
    discard = next(connection)

    for group in groups(connection, lambda acq: acq.isFlagSet(ismrmrd.ACQ_LAST_IN_SLICE)):
        image = process_group(group, config, params)

        logging.info("Sending image to client:\n%s", image)
        connection.send_image(image)


def process_group(group, config, params):

    data = [acquisition.data for acquisition in group]

    logging.info("Processing %d acquisitions.", len(data))

    data = np.stack(data, axis=-1)
    data = fft.fftshift(data, axes=(1, 2))
    data = fft.ifft2(data)
    data = fft.ifftshift(data, axes=(1, 2))
    data = np.abs(data)

    data = np.square(data)
    data = np.sum(data, axis=0)
    data = np.sqrt(data)

    return ismrmrd.Image.from_array(data, acquisition=group[0])


