#!/usr/bin/env python

import numpy as np

learning_data_filename = "./out.npz"
data = np.load(learning_data_filename)
weight = data['weight']

print(weight)
