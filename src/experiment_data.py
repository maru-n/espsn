#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from os.path import join, splitext
from scipy.signal import argrelmax
import util
import ipdb


class ESPSNExperimentData(object):

    def __init__(self, setting_file, log_file):
        super(ESPSNExperimentData, self).__init__()
        self.__read_setting_file(setting_file)
        self.__read_log_file(log_file)


    # call this after __read_setting_file()
    def __read_log_file(self, log_file):
        """
        N = self.settings["N"]
        duration = self.settings["duration"]
        esn_dt = self.settings["esn_dt"]
        input_num = self.settings["input_num"]

        #time_step = int(duration/esn_dt)
        #self.esn_time = np.array([s*esn_dt for s in range(int(duration/esn_dt))])
        """

        self.cwnd = {}
        for src, dst, _, _ in self.settings["topology"]:
            if not src in self.cwnd:
                self.cwnd[src] = {}
            self.cwnd[src][dst] = []

        log_len = len([None for l in open(log_file)])
        for i, l in enumerate(open(log_file)):
            d = l.split()
            src = int(d[1])
            dst = int(d[3])
            time = float(d[0])
            cwnd = float(d[6])
            self.cwnd[src][dst].append((time, cwnd))
            if i % 1000 == 0:
                util.print_status("\r %d/%d"%(i, log_len), end="", header="")
        print("")

        esn_dt = self.settings["esn_dt"]
        duration = self.settings["duration"]
        self.esn_time_index = np.arange(0, duration, esn_dt)
        self.esn_cwnd_index = []
        self.esn_cwnd = np.zeros((len(self.esn_time_index), len(self.settings["topology"])))
        i = 0
        for src in self.cwnd:
            for dst in self.cwnd[src]:
                self.esn_cwnd_index.append((src,dst))
                for time, cwnd in self.cwnd[src][dst]:
                    time_idx = int(time/esn_dt)
                    self.esn_cwnd[time_idx:,i] = cwnd
                i += 1



        """
        cwnd_raw_matrix = [[[] for j in range(N)] for i in range(N)]
        cwnd_matrix = [[np.zeros(int(duration/esn_dt)) for j in range(N)] for i in range(N)]
        print_time = 0
        for l in open(log_file):
            d = l.split()
            src = int(d[1])
            dst = int(d[3])
            time = float(d[0])
            cwnd = float(d[6])
            cwnd_raw_matrix[src][dst].append((time, cwnd))
            cwnd_matrix[src][dst][int(time/esn_dt):] = cwnd
            if print_time < time:
                util.print_status("\r %d/%d"%(int(print_time), duration), end="", header="")
                print_time += 10


        self.cwnd = []
        self.cwnd_raw = []
        self.cwnd_src_dst = []

        for i in range(N):
            for j in range(N):
                #c = np.array(cwnd_raw_matrix[i][j])
                c = np.array(cwnd_matrix[i][j])
                if not np.any(c):
                    continue
                self.cwnd.append(c)

                c = np.array(cwnd_raw_matrix[i][j])
                peak_idx = argrelmax(c[:, 1])
                time = c[peak_idx, 0][0,:]
                cwnd = c[peak_idx, 1][0,:]
                #self.cwnd.append(np.interp(self.time, time, cwnd))
                self.cwnd_raw.append(c)

                self.cwnd_src_dst.append((i,j))
        self.cwnd = np.array(self.cwnd)

        #dmax = self.cwnd.max()
        #dmin = self.cwnd.min()
        #norm_cwnd = (self.cwnd-dmin).astype(float) / (dmax-dmin).astype(float)
        #self.cwnd = norm_cwnd

        print("")
        """

    def __read_setting_file(self, setting_file):
        sf = open(setting_file, 'r')
        """
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
        """
        self.settings ={}
        while True:
            line = sf.readline()
            if line == '\n':
                break
            prop, val = line.strip("\n").split(':')
            if prop in ['N', 'duration', 'input_num']:
                self.settings[prop] = int(val)
            elif prop in ['k', 'esn_init_time', 'esn_training_time', 'esn_dt']:
                self.settings[prop] = float(val)
            elif prop in ['continuous']:
                self.settings[prop] = bool(val)
            elif prop in ['link_bps', 'link_delay', 'link_queue']:
                self.settings[prop] = val
            else:
                raise Exception("Invalid property: " + prop)


        self.settings['topology'] = []
        while True:
            line = sf.readline()
            if not line.strip():
                break
            src, dst, input_ch, pos_neg = [int(d) for d in line.split()]
            self.settings['topology'].append((src, dst, input_ch, pos_neg))


        self.settings['input'] = []
        self.settings['input_continuous'] = []
        self.settings['target'] = []

        #duration = self.settings['duration']
        #dt = self.settings['esn_dt']
        is_continuous = self.settings['continuous']
        input_num = self.settings['input_num']
        #esn_data_dim = duration / dt
        #self.esn_target = np.zeros(esn_data_dim)
        self.esn_target = []

        while True:
            line = sf.readline()
            if not line.strip():
                break
            value_str = line.split()
            time = float(value_str[0])

            input_bin_list = [int(v) for v in value_str[1:1+input_num]]
            self.settings['input'].append([time] + input_bin_list)

            if is_continuous and len(value_str)==(2+2*input_num):
                input_continuous_list = [float(v) for v in value_str[1+input_num:1+input_num*2]]
                target = float(value_str[-1])
                self.settings['input_continuous'].append([time] + input_continuous_list)
                self.settings['target'].append([time, target])
                self.esn_target.append(target)

            if not is_continuous:
                target = float(value_str[-1])
                self.settings['target'].append([time, target])
                self.esn_target.append(target)
                # when esn_dt !== signal_duration
                #esn_data_idx = int(time / dt)
                #self.esn_target[esn_data_idx:] = target


        """
        duration = self.settings['duration']
        dt = self.settings['esn_dt']
        cnt = duration / dt
        self.time = np.linspace(0., duration, dt)
        self.target = np.zeros(time_cnt)
        self.input = np.zeros((time_cnt, input_num))
        for line in sf:
            d = line.split()
            time = float(d[0])
            time_idx = int(time / esn_dt)
            #input_raw = d[-2]
            #self.input_raw.append((time, input_raw))
            #self.target[time_idx:] = int(d[-1])
            self.target[time_idx:] = d[-1]
            for i in range(input_num):
                self.input[i][time_idx:] = int(d[i+1])
        """
        sf.close()
