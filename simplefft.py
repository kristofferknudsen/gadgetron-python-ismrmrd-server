
import ismrmrd

import itertools
import logging
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt


def groups(iterator, predicate):
    group = []
    for item in iterator:
        group.append(item)

        if predicate(item):
            yield group
            group = []


def process(connection, config, params):
    logging.info("Processing connection.")
    logging.info("Config: \n%s", config)
    logging.info("Params: \n%s", params)

    for group in groups(connection, lambda acq: acq.isFlagSet(ismrmrd.ACQ_LAST_IN_SLICE)):
        logging.info(len(group))
        logging.info(group)

        process_group(group, config, params)


def process_group(group, config, params):

    data = [acquisition.data for acquisition in group]

    logging.info("Received %d acquisitions.", len(data))

    data = np.stack(data, axis=-1)
    data = fft.fftshift(data, axes=(1, 2))
    data = fft.ifft2(data)
    data = fft.ifftshift(data, axes=(1, 2))
    data = np.abs(data)

    data = np.square(data)
    data = np.sum(data, axis=0)
    data = np.sqrt(data)

    print(data)

    plt.imshow(data)
    plt.show()


