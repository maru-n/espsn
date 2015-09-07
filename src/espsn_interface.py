#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from numpy import dot, eye
from numpy.linalg import inv
import sys
import json
from os.path import join, splitext
import pdb


USE_PEAK = False

#
# t ----------------------------------------->
#    init  |   training   |    test         |
#       init_time      training_time    duration
#
class ESPSNExperimentData(object):

    def __init__(self, setting_file, tcp_cwnd_log_file):
        super(ESPSNExperimentData, self).__init__()
        self.settings = self.__read_setting_file(setting_file)

        N = self.settings["N"]
        duration = self.settings["duration"]
        esn_dt = self.settings["esn_dt"]
        input_num = self.settings["input_num"]

        self.time = np.array([s*esn_dt for s in range(int(duration/esn_dt))])
        time_cnt = len(self.time)

        # read target signale and input signals from setting file
        self.target = np.zeros(time_cnt)
        self.input = [np.zeros(time_cnt) for i in range(input_num)]
        for d in np.loadtxt(setting_file, skiprows=10):
            time = float(d[0])
            time_idx = int(time / esn_dt)
            self.target[time_idx:] = int(d[-1])
            for i in range(input_num):
                self.input[i][time_idx:] = int(d[i+1])

        # read cwnd output data from tcp file
        cwnd_cnt = N * N - N
        self.cwnd = np.zeros((cwnd_cnt, time_cnt))
        #TODO:
        #cnt = np.ones((cwnd_cnt, time_cnt))

        if splitext(tcp_cwnd_log_file)[1] == ".npy":
            self.cwnd = np.load(tcp_cwnd_log_file)
        else:
            #for d in np.loadtxt(tcp_cwnd_log_file, usecols=(0, 1, 3, 6)):
            for d in np.loadtxt(tcp_cwnd_log_file, usecols=(1, 3, 7, 17)):
                src = int(d[1])
                dst = int(d[2])
                time = float(d[0])
                cwnd = float(d[3])
                if src == dst or not(0 <= src < N) or not(0 <= dst < N):
                    continue
                idx = src * N + dst
                if src < dst:
                    idx = idx - src - 1
                else:
                    idx = idx - src

                time_idx = int(time / esn_dt)

                if 0 <= time_idx:
                    self.cwnd[idx, time_idx:] = float(cwnd)
                    #self.cwnd[idx, time_idx:] += float(cwnd)
                    #cnt[idx, time_idx:] += float(1)

        #self.cwnd = self.cwnd / cnt

        dmax = self.cwnd.max()
        dmin = self.cwnd.min()
        norm_cwnd = (self.cwnd-dmin).astype(float) / (dmax-dmin).astype(float)
        self.cwnd = norm_cwnd

        if USE_PEAK:
            cwnd_peak = []
            for c in self.cwnd:
                local_max = np.r_[True, c[1:] >= c[:-1]] & np.r_[c[:-1] >= c[1:], True]
                peak_list = [c for c, b in zip(c, local_max) if b]
                peak_time = [t for t, b in zip(self.time, local_max) if b]
                peak_series = np.interp(self.time, peak_time, peak_list)
                cwnd_peak.append(peak_series)
            self.cwnd_peak = np.array(cwnd_peak)

    def __read_setting_file(self, setting_file):
        sf = open(setting_file, 'r')
        N = int(sf.readline().rstrip("\n").split(':')[1])
        duration = int(sf.readline().rstrip("\n").split(':')[1])
        link_bps = sf.readline().rstrip("\n").split(':')[1]
        link_delay = sf.readline().rstrip("\n").split(':')[1]
        link_queue = sf.readline().rstrip("\n").split(':')[1]
        init_time = float(sf.readline().rstrip("\n").split(':')[1])
        training_time = float(sf.readline().rstrip("\n").split(':')[1])
        esn_dt = float(sf.readline().rstrip("\n").split(':')[1])
        input_num = int(sf.readline().rstrip("\n").split(':')[1])
        sf.close()
        settings = {
            "N": N,
            "duration": duration,
            "link_bps": link_bps,
            "link_delay": link_delay,
            "link_queue": link_queue,
            "init_time": init_time,
            "training_time": training_time,
            "esn_dt": esn_dt,
            "input_num": input_num
        }
        return settings


def train_weight(output_data, instruction_data, reg_coef=1e-8):
    X = output_data
    Yt = instruction_data
    Wout = dot(dot(Yt, X.T), inv(dot(X, X.T) + reg_coef * eye(X.shape[0])))
    #Wout = dot( dot(Yt,X.T), linalg.inv( dot(X,X.T)))
    return Wout

def train_weight_and_reg_coef_search(experimant_data, reg_coefs=np.arange(0.1, 2.0, 0.1)):
    init_time = experimant_data.settings["init_time"]
    training_time = experimant_data.settings["training_time"]
    esn_dt = experimant_data.settings["esn_dt"]
    start_time_idx = int(init_time / esn_dt)
    end_time_idx = int(training_time / esn_dt)

    if USE_PEAK:
        cwnd4training = experimant_data.cwnd_peak[:, start_time_idx:end_time_idx]
    else:
        cwnd4training = experimant_data.cwnd[:, start_time_idx:end_time_idx]
    target4training = experimant_data.target[start_time_idx:end_time_idx]
    target4validation = experimant_data.target[end_time_idx:]

    search_result_mse = []
    best_mse = 1000
    best_weight = None
    best_output = None
    for reg_coef in reg_coefs:
        weight = train_weight(cwnd4training, target4training, reg_coef=reg_coef)
        if USE_PEAK:
            output = dot(weight, experimant_data.cwnd_peak)
        else:
            output = dot(weight, experimant_data.cwnd)
        output4validation = output[end_time_idx:]
        mse = sum(np.square(output4validation - target4validation)) / len(output4validation)
        print_status("reg_coef: %12.10f  / MSE: %f" % (reg_coef, mse))

        if best_mse > mse:
            best_mse = mse
            best_regcoef = reg_coef
            best_output = output
            best_weight = weight

        search_result_mse.append(mse)

    return best_mse, best_weight, best_output, best_regcoef, search_result_mse


def print_status(msg):
    print("\033[34m[ESN]\033[39m " + msg)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("espsn_interface.py SETTING_FILE {TCP_LOG_FILE|CWND_NPY_FILE} [OUTPUT_PREFIX]")

    if len(sys.argv) >= 4:
        output_prefix = sys.argv[3]
    else:
        output_prefix = "./out"
    output_prefix = output_prefix + "."

    print_status("reading settings and data...")
    data = ESPSNExperimentData(sys.argv[1], sys.argv[2])

    print_status("training wegihts...")
    reg_coefs = np.arange(0.1, 2.0, 0.1)
    best_mse, best_weight, best_output, best_regcoef, search_result_mse = train_weight_and_reg_coef_search(data, reg_coefs)

    print_status("saving result...")
    np.save((output_prefix + "time"), data.time)
    np.save((output_prefix + "cwnd"), data.cwnd)
    if USE_PEAK:
        np.save((output_prefix + "cwnd_peak"), data.cwnd_peak)
    np.save((output_prefix + "target"), data.target)
    np.save((output_prefix + "input"), data.input)

    np.save((output_prefix + "weight"), best_weight)
    np.save((output_prefix + "output"), best_output)

    np.save((output_prefix + "search_regcoef"), reg_coefs)
    np.save((output_prefix + "search_mse"), search_result_mse)

    data.settings["reg_coef"] = best_regcoef
    data.settings["mse"] = best_mse
    setting_file = open((output_prefix + "settings.json"), "w")
    setting_file.write(json.dumps(data.settings))
