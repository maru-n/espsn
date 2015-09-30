#!/usr/bin/env python

import json
import numpy as np
import glob
from os import path
data_dir = "../scripts/k_search/"

def fetch_k_mse_data(data_dir):
    settings_files = glob.glob(path.join(data_dir, '*settings.json'))
    mse_list = []
    k_list = []

    for settingf  in settings_files:
        settings = json.load(open(settingf))
        mse_list.append(settings["mse"])
        k_list.append(int(settings["k"]))
    return k_list, mse_list

import sys

if __name__ == '__main__':
    for data_dir in sys.argv[1:]:
        print(data_dir)
        k_list, mse_list = fetch_k_mse_data(data_dir)
        #print(k_list)
        #print(mse_list)
        np.save(data_dir+"_k.npy", k_list)
        np.save(data_dir+"_mse.npy", mse_list)
