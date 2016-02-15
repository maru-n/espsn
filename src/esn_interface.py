#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
from numpy import dot, eye
from numpy.linalg import inv
from experiment_data import ESPSNExperimentData
import util

def train_weight(output_data, instruction_data, reg_coef=1e-8):
    X = output_data
    Yt = instruction_data
    Y = instruction_data
    alpha = reg_coef
    #import ipdb; ipdb.set_trace()

    try:
        Wout = dot(inv(dot(X.T, X) + alpha * eye(X.shape[1])), dot(X.T, Y))
    except Exception as e:
    #except LinAlgError as e:
        util.print_status("!!! Singular matrix !!!")
        Wout = np.ones(X.shape[1])

    #Wout = dot(dot(Yt, X.T), inv(dot(X, X.T) + reg_coef * eye(X.shape[0])))
    #Wout = dot( dot(Yt,X.T), linalg.inv( dot(X,X.T)))
    return Wout

def train_weight_and_reg_coef_search(experimant_data, reg_coefs=np.arange(0.1, 2.0, 0.1)):
    init_time = experimant_data.settings["esn_init_time"]
    training_time = experimant_data.settings["esn_training_time"]
    esn_dt = experimant_data.settings["esn_dt"]
    start_time_idx = int(init_time / esn_dt)
    end_time_idx = int(training_time / esn_dt)

    cwnd4training = experimant_data.esn_cwnd[start_time_idx:end_time_idx, :]
    #cwnd4training = experimant_data.esn_cwnd[start_time_idx:end_time_idx, :].T
    #cwnd4training = experimant_data.cwnd_raw[:, start_time_idx:end_time_idx]
    target4training = experimant_data.esn_target[start_time_idx:end_time_idx]
    target4validation = experimant_data.esn_target[end_time_idx:]

    search_result_mse = []
    best_mse = 1000
    best_weight = None
    best_output = None
    best_regcoef = None
    for reg_coef in reg_coefs:
        weight = train_weight(cwnd4training, target4training, reg_coef=reg_coef)
        output = dot(experimant_data.esn_cwnd, weight)
        #output = dot(weight, experimant_data.esn_cwnd)
        #output = dot(weight, experimant_data.esn_cwnd.T)
        output4validation = output[end_time_idx:]
        mse = sum(np.square(output4validation - target4validation)) / len(output4validation)
        util.print_status("reg_coef: %f  / MSE: %f" % (reg_coef, mse), header="")

        if best_mse > mse:
            best_mse = mse
            best_regcoef = reg_coef
            best_output = output
            best_weight = weight

        search_result_mse.append(mse)
    return best_mse, best_weight, best_output, best_regcoef, search_result_mse


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("espsn_interface.py SETTING_FILE {TCP_LOG_FILE|CWND_NPY_FILE} [OUTPUT_PREFIX]")

    if len(sys.argv) >= 4:
        output_filename = sys.argv[3]
    else:
        output_filename = "./out"

    util.print_status("parsing experiment data...")
    data = ESPSNExperimentData(sys.argv[1], sys.argv[2])

    util.print_status("training wegihts...")
    reg_coefs = np.arange(1.0, 10.0, 1.0)

    best_mse, best_weight, best_output, best_regcoef, search_result_mse = train_weight_and_reg_coef_search(data, reg_coefs)

    util.print_status("saving result...")
    np.savez(output_filename,
             esn_time_index    = data.esn_time_index,
             #esn_cwnd_index    = data.esn_cwnd_index,
             esn_cwnd          = data.esn_cwnd,
             esn_target        = data.esn_target,
             cwnd              = data.cwnd,
             #cwnd_raw = data.cwnd_raw,
             #cwnd_src_dst = data.cwnd_src_dst,
             #input_raw = data.input_raw,
             weight            = best_weight,
             output            = best_output,
             reg_coef          = best_regcoef,
             mse               = best_mse,
             search_regcoef    = reg_coefs,
             search_mse        = search_result_mse,
             target            = data.settings['target'],
             input             = data.settings['input'],
             input_continuous  = data.settings['input_continuous'],
             continuous        = data.settings['continuous'],
             N                 = data.settings['N'],
             k                 = data.settings['k'],
             duration          = data.settings['duration'],
             link_bps          = data.settings['link_bps'],
             link_delay        = data.settings['link_delay'],
             link_queue        = data.settings['link_queue'],
             esn_init_time     = data.settings['esn_init_time'],
             esn_training_time = data.settings['esn_training_time'],
             esn_dt            = data.settings['esn_dt'],
             input_num         = data.settings['input_num'],
             topology          = data.settings['topology']
             )
