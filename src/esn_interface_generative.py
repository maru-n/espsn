#!/usr/bin/env python

import random
import numpy as np
import sys
import os
import util
#from experiment_data import ESPSNExperimentData

log = open("../generative.log", "w")
log.write("=========================\n")

training_data_filename = sys.stdin.readline().strip()
data = np.load(training_data_filename)
log.write("training_data_filename: " + training_data_filename+"\n")

tcp_filename = sys.stdin.readline().strip()
tcp_file = open(tcp_filename, "w")

activity_filename = sys.stdin.readline().strip()
activity_file = open(activity_filename, "w")
log.write("activity_filename: " + activity_filename+"\n")

weight = data['weight']
N = data['N']
predictive_input = data['input_continuous'][:,1]
log.write("predictive input: " + str(predictive_input) + "\n")



topology = data['topology']
current_cwnd = np.zeros(len(topology))

data_idx = 0
init_idx = 0

time = 0.0
while True:
    line = sys.stdin.readline().strip()
    log.write("received message: " + line+"\n")
    if(line == "update"):
        x = np.dot(current_cwnd, weight)
        activity_file.write(str(x)+'\n')

        # for debug: correct data
        #x = predictive_input[data_idx]
        #data_idx += 1

        # output to ns-2
        pwm_duty = util.continuous_pwm_func(x)
        sys.stdout.write("%f\n" % (pwm_duty))
        """
        if(init_idx < 100):
            print(0.5)
            init_idx += 1
        else:
            print(x)
        """
        sys.stdout.flush()

    elif(line == "clean\n"):
        break
    elif "cwnd_" in line:
        tcp_file.write(line + "\n")
        vals = line.split()
        log.write(str(vals) + "\n")
        time = float(vals[0])
        src = int(vals[1])
        dst = int(vals[3])
        cwnd = float(vals[6])
        for i,(s, d, ch, pos_neg) in enumerate(topology):
            if s==src and d==dst:
                current_cwnd[i] = cwnd
    else:
        break
