#  Developed by Joseph M. Conti and Joseph W. Boardman on 1/21/19 6:29 PM.
#  Last modified 1/21/19 6:29 PM
#  Copyright (c) 2019. All rights reserved.

import numpy as np

if __name__ == "__main__":

    data = np.arange(1.0, 10.0)
    print("data start: ", data)

    low_masked = np.ma.masked_where(data < 3, data, False)
    low_mask = np.ma.getmask(low_masked)
    print("low_masked: ", low_masked)
    print("low_mask: ", low_mask)
    print("data: ", data)

    high_masked = np.ma.masked_where(data > 7 , data, False)
    high_mask = np.ma.getmask(high_masked)
    print("high_masked: ", high_masked)
    print("high_mask: ", high_mask)
    print("data: ", data)

    full_mask = low_mask | high_mask
    print("full_mask: ", full_mask)

    data_masked = np.ma.masked_where(full_mask, data)
    print("data_masked: ", data_masked)
    # size gives total number of elements in the array ignoring masking
    print("data_masked size: ", data_masked.size)
    # count() gives number of unmasked elements
    print("data_masked count: ", data_masked.count())

    data_masked = data_masked * 3
    print(data_masked)

    data_masked[low_mask] = 0
    data_masked[high_mask] = 255
    print("data_adj: ", data_masked)
