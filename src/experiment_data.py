#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from os.path import join, splitext
from scipy.signal import argrelmax
import util


class ESPSNExperimentData(object):

    def __init__(self, setting_file, tcp_cwnd_log_file):
        super(ESPSNExperimentData, self).__init__()
        self.__read_setting_file(setting_file)

        N = self.settings["N"]
        duration = self.settings["duration"]
        esn_dt = self.settings["esn_dt"]
        input_num = self.settings["input_num"]

        self.time = np.array([s*esn_dt for s in range(int(duration/esn_dt))])

        cwnd_tmp = np.zeros((N * N - N, len(self.time)))
        cwnd_raw_matrix = [[[] for j in range(N)] for i in range(N)]
        print_time = 0
        for l in open(tcp_cwnd_log_file):
            d = l.split()
            src = int(d[1])
            dst = int(d[3])
            time = float(d[0])
            cwnd = float(d[6])
            cwnd_raw_matrix[src][dst].append((time, cwnd))
            if print_time < time:
                util.print_status("time: %f" % print_time, header="")
                print_time += 200
        self.cwnd = []
        self.cwnd_raw = []
        self.cwnd_src_dst = []

        for i in range(N):
            for j in range(N):
                c = np.array(cwnd_raw_matrix[i][j])
                if not np.any(c):
                    continue
                peak_idx = argrelmax(c[:, 1])
                time = c[peak_idx, 0][0,:]
                cwnd = c[peak_idx, 1][0,:]
                self.cwnd.append(np.interp(self.time, time, cwnd))
                self.cwnd_raw.append(c)
                self.cwnd_src_dst.append((i,j))
        self.cwnd = np.array(self.cwnd)

        dmax = self.cwnd.max()
        dmin = self.cwnd.min()
        norm_cwnd = (self.cwnd-dmin).astype(float) / (dmax-dmin).astype(float)
        self.cwnd = norm_cwnd


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

        self.settings = {
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
        sf.readline()

        self.topology = []
        while True:
            line = sf.readline()
            if line == "\n":
                break
            self.topology.append([int(d) for d in line.split()])

        time_cnt = duration/esn_dt

        self.target = np.zeros(time_cnt)
        self.input_raw = []
        self.input = np.zeros((input_num, time_cnt))
        for line in sf:
            d = line.split()
            time = float(d[0])
            time_idx = int(time / esn_dt)
            input_raw = d[-2]
            self.input_raw.append((time, input_raw))
            #self.target[time_idx:] = int(d[-1])
            self.target[time_idx:] = d[-1]
            for i in range(input_num):
                self.input[i][time_idx:] = int(d[i+1])

        sf.close()
