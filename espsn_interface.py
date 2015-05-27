#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from numpy import dot, eye
from numpy.linalg import inv
import sys
import json


#
# t ----------------------------------------->
#    init  |   training   |    test         |
#       init_time      training_time    duration
#
class ESPSNExperimentData(object):

    def __init__(self, setting_file, tcp_log_file):
        super(ESPSNExperimentData, self).__init__()

        # read settings
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
        self.settings = {
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
        sf.close()

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
        for d in np.loadtxt(tcp_log_file, usecols=(1, 3, 7, 17)):
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
                self.cwnd[idx, time_idx:] = cwnd


def train_weight(data, instruction, reg_coef=1e-8):
    X = data
    Yt = instruction
    Wout = dot(dot(Yt, X.T), inv(dot(X, X.T) + reg_coef * eye(X.shape[0])))
    #Wout = dot( dot(Yt,X.T), linalg.inv( dot(X,X.T)))
    return Wout


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "espsn_interface.py SETTING_FILE TCP_LOG_FILE [OUTPUT_PREFIX]"
    print "reading settings and data..."
    data = ESPSNExperimentData(sys.argv[1], sys.argv[2])
    if len(sys.argv) >= 4:
        output_prefix = sys.argv[3]
    else:
        output_prefix = ""

    print "training wegihts..."
    init_time = data.settings["init_time"]
    training_time = data.settings["training_time"]
    esn_dt = data.settings["esn_dt"]
    start_time_idx = int(init_time / esn_dt)
    end_time_idx = int(training_time / esn_dt)
    cwnd4training = data.cwnd[:, start_time_idx:end_time_idx]
    target4training = data.target[start_time_idx:end_time_idx]
    weight = train_weight(cwnd4training, target4training)

    output = dot(weight, data.cwnd)

    np.save(output_prefix+"time", data.time)
    np.save(output_prefix+"cwnd", data.cwnd)
    np.save(output_prefix+"weight", weight)
    np.save(output_prefix+"target", data.target)
    np.save(output_prefix+"input", data.input)
    np.save(output_prefix+"output", output)

    setting_file = open(output_prefix+"settings.json", "w")
    setting_file.write(json.dumps(data.settings))
