#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from numpy import dot, eye
from numpy.linalg import inv
import sys
import json
from os.path import join, splitext
from scipy.signal import argrelmax
import pdb


#USE_PEAK = False

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
        self.input_raw = []
        self.input = [np.zeros(time_cnt) for i in range(input_num)]
        for d in np.loadtxt(setting_file, skiprows=10):
            time = float(d[0])
            time_idx = int(time / esn_dt)
            input_raw = d[-2]
            self.input_raw.append((time, input_raw))
            #self.target[time_idx:] = int(d[-1])
            self.target[time_idx:] = d[-1]
            for i in range(input_num):
                self.input[i][time_idx:] = int(d[i+1])

        # read cwnd output data from tcp file
        cwnd_cnt = N * N - N

        cwnd_tmp = np.zeros((cwnd_cnt, time_cnt))
        #self.cwnd = np.zeros((cwnd_cnt, time_cnt))

        if splitext(tcp_cwnd_log_file)[1] == ".npy":
            cwnd_tmp = np.load(tcp_cwnd_log_file)
        else:
            cwnd_raw_matrix = [[[] for j in range(N)] for i in range(N)]
            print_time = 0
            #for d in pd.read_csv(tcp_cwnd_log_file, sep=' ', header=None):
            #for d in np.loadtxt(tcp_cwnd_log_file, usecols=(0, 1, 3, 6)):
                # src = int(d[1])
                # dst = int(d[2])
                # time = float(d[0])
                # cwnd = float(d[3])
            for l in open(tcp_cwnd_log_file):
                d = l.split()
                src = int(d[1])
                dst = int(d[3])
                time = float(d[0])
                cwnd = float(d[6])
                cwnd_raw_matrix[src][dst].append((time, cwnd))
                if print_time < time:
                    print_status("time: %f" % print_time, header="")
                    print_time += 200
            self.cwnd = []
            self.cwnd_raw = []
            self.cwnd_src_dst = []
            #self.cwnd_raw = []
            for i in range(N):
                for j in range(N):
                    c = np.array(cwnd_raw_matrix[i][j])
                    if not np.any(c):
                        continue
                    peak_idx = argrelmax(c[:, 1])
                    time = c[peak_idx, 0][0,:]
                    cwnd = c[peak_idx, 1][0,:]
                    self.cwnd.append( np.interp(self.time, time, cwnd))
                    self.cwnd_raw.append(c)
                    self.cwnd_src_dst.append((i,j))
                    #self.cwnd_raw.append()
                    #peak_series = np.interp(self.time, peak_time, peak_list)
                    #cwnd_raw[i][j] =
            self.cwnd = np.array(self.cwnd)


            """
            print_time = 0
            for d in np.loadtxt(tcp_cwnd_log_file, usecols=(0, 1, 3, 6)):
            #for d in np.loadtxt(tcp_cwnd_log_file, usecols=(1, 3, 7, 17)):
                src = int(d[1])
                dst = int(d[2])
                time = float(d[0])
                cwnd = float(d[3])
                if print_time < time:
                    print_status("time: %f" % print_time, header="       ")
                    print_time += 100
                if src == dst or not(0 <= src < N) or not(0 <= dst < N):
                    continue
                idx = src * N + dst
                if src < dst:
                    idx = idx - src - 1
                else:
                    idx = idx - src

                time_idx = int(time / esn_dt)

                if 0 <= time_idx:
                    cwnd_tmp[idx, time_idx:] = float(cwnd)

            self.cwnd = []
            for c in cwnd_tmp:
                if np.any(c):
                    self.cwnd.append(c)
            self.cwnd = np.array(self.cwnd)
            """

        #self.cwnd = self.cwnd / cnt

        dmax = self.cwnd.max()
        dmin = self.cwnd.min()
        norm_cwnd = (self.cwnd-dmin).astype(float) / (dmax-dmin).astype(float)
        self.cwnd = norm_cwnd
        """
        if USE_PEAK:
            cwnd_peak = []
            for c in self.cwnd:
                local_max = np.r_[True, c[1:] >= c[:-1]] & np.r_[c[:-1] >= c[1:], True]
                peak_list = [c for c, b in zip(c, local_max) if b]
                peak_time = [t for t, b in zip(self.time, local_max) if b]
                peak_series = np.interp(self.time, peak_time, peak_list)
                cwnd_peak.append(peak_series)
            self.cwnd_peak = np.array(cwnd_peak)
        """

    def __read_setting_file(self, setting_file):
        sf = open(setting_file, 'r')
        N = int(sf.readline().rstrip("\n").split(':')[1])
        duration = int(sf.readline().rstrip("\n").split(':')[1])
        link_bps = sf.readline().rstrip("\n").split(':')[1]
        link_delay = sf.readline().rstrip("\n").split(':')[1]
        link_queue = sf.readline().rstrip("\n").split(':')[1]
        k = float(sf.readline().rstrip("\n").split(':')[1])
        init_time = float(sf.readline().rstrip("\n").split(':')[1])
        training_time = float(sf.readline().rstrip("\n").split(':')[1])
        esn_dt = float(sf.readline().rstrip("\n").split(':')[1])
        input_num = int(sf.readline().rstrip("\n").split(':')[1])
        sf.close()
        settings = {
            "N": N,
            "k": k,
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

    cwnd4training = experimant_data.cwnd[:, start_time_idx:end_time_idx]
    target4training = experimant_data.target[start_time_idx:end_time_idx]
    target4validation = experimant_data.target[end_time_idx:]

    search_result_mse = []
    best_mse = 1000
    best_weight = None
    best_output = None
    best_regcoef = None
    for reg_coef in reg_coefs:
        weight = train_weight(cwnd4training, target4training, reg_coef=reg_coef)
        output = dot(weight, experimant_data.cwnd)
        output4validation = output[end_time_idx:]
        mse = sum(np.square(output4validation - target4validation)) / len(output4validation)
        print_status("reg_coef: %f  / MSE: %f" % (reg_coef, mse), header="")

        if best_mse > mse:
            best_mse = mse
            best_regcoef = reg_coef
            best_output = output
            best_weight = weight

        search_result_mse.append(mse)

    return best_mse, best_weight, best_output, best_regcoef, search_result_mse


def print_status(msg, header="[ESN]"):
    print("\033[34m" + header + "\033[39m " + msg)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("espsn_interface.py SETTING_FILE {TCP_LOG_FILE|CWND_NPY_FILE} [OUTPUT_PREFIX]")

    if len(sys.argv) >= 4:
        output_filename = sys.argv[3]
    else:
        output_filename = "./out"

    print_status("reading settings and data...")
    data = ESPSNExperimentData(sys.argv[1], sys.argv[2])

    print_status("training wegihts...")
    reg_coefs = np.arange(0.0, 10.0, 1.0)

    best_mse, best_weight, best_output, best_regcoef, search_result_mse = train_weight_and_reg_coef_search(data, reg_coefs)

    print_status("saving result...")
    np.savez(output_filename,
             time = data.time,
             cwnd = data.cwnd,
             cwnd_raw = data.cwnd_raw,
             cwnd_src_dst = data.cwnd_src_dst,
             target = data.target,
             input = data.input,
             input_raw = data.input_raw,
             weight = best_weight,
             output = best_output,
             reg_coef = best_regcoef,
             mse = best_mse,
             search_regcoef = reg_coefs,
             search_mse = search_result_mse,
             N = data.settings['N'],
             k = data.settings['k'],
             duration = data.settings['duration'],
             link_bps = data.settings['link_bps'],
             link_delay = data.settings['link_delay'],
             link_queue = data.settings['link_queue'],
             init_time = data.settings['init_time'],
             training_time = data.settings['training_time'],
             esn_dt = data.settings['esn_dt'],
             input_num = data.settings['input_num'],
             )
