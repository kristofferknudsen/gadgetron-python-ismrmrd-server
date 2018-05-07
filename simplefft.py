
import ismrmrd

import itertools
import logging
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt


async def groups(iterator, predicate):
    group = []
    async for item in iterator:
        group.append(item)

        if predicate(item):
            yield group
            group = []


async def process(connection, config, params):
    logging.info("Processing connection.")
    logging.info("Config: \n%s", config)
    logging.info("Params: \n%s", params)

    async for group in groups(connection, lambda acq: acq.isFlagSet(ismrmrd.ACQ_LAST_IN_SLICE)):
        process_group(group, config, params)


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

    plt.imshow(data)
    plt.show()


