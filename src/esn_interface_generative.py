#!/usr/bin/env python

import random
import numpy as np
import sys
from experiment_data import ESPSNExperimentData

training_data_filename = sys.stdin.readline().strip()
training_data = np.load(training_data_filename)

tcp_filename = sys.stdin.readline().strip()
tcp_file = open(tcp_filename, "w")

activity_filename = sys.stdin.readline().strip()
activity_file = open(activity_filename, "w")

#setting_filename = "../setting.txt"
#sys.stderr.write(str(weight.shape))

weight = training_data['weight']
esn_dt = training_data['esn_dt']
N = training_data['N']

cwnd_src_dst = training_data['cwnd_src_dst']
current_cwnd = np.zeros(cwnd_src_dst.shape[0])
output = []

correct_data = np.loadtxt("../MackeyGlass_t17.txt")
data_idx = 0
init_idx = 0

output_time = 0.0
time = 0.0
while True:
    line = sys.stdin.readline()
    tcp_file.write(line)
    if(line == "get_activity\n"):
        x = np.dot(current_cwnd, weight)/40.0
        correct_x = correct_data[data_idx] + 0.6
        data_idx += 1

        if(init_idx < 10):
            print(0.1)
            init_idx += 1
        else:
            #print(x)
            print(0.1)
        #print(correct_x)
        sys.stdout.flush()
        output.append(x)
        activity_file.write(str(x)+'\n')
    elif(line == "clean\n"):
        break
    else:
        vals = line.split()
        time = float(vals[0])
        src = int(vals[1])
        dst = int(vals[3])
        cwnd = float(vals[6])
        for i,v in enumerate(cwnd_src_dst):
            if v[0]==src and v[1]==dst:
                current_cwnd[i] = cwnd

"""
tcp_file.close()
output_filename = "out"

util.print_status("reading settings and data...")
data = ESPSNExperimentData(setting_filename, tcp_filename)

util.print_status("saving result...")
np.savez(output_filename,
         time = data.time,
         cwnd = data.cwnd,
         cwnd_raw = data.cwnd_raw,
         cwnd_src_dst = data.cwnd_src_dst,
         target = data.target,
         input = data.input,
         input_raw = data.input_raw,
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
         topology = data.topology
         )
"""
