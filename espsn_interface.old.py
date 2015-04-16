#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A minimalistic Echo State Networks demo with Mackey-Glass (delay 17) data
in "plain" scientific Python.
by Mantas LukoÅ¡eviÄ?ius 2012
http://minds.jacobs-university.de/mantas
"""
import numpy as np
from numpy import dot, eye, linalg
import matplotlib.pyplot as plt
from matplotlib.mlab import frange
#from scipy import linalg
import sys


def convert_cwnd_matrix(raw_data):
    N = int(np.max(raw_data[:, 1]))+1
    cwnd = [[np.empty((0, 2)) for i in range(N)] for j in range(N)]
    for d in raw_data:
        src = int(d[1])
        dst = int(d[2])
        if src == dst or not(0 <= src < N) or not(0 <= dst < N):
            continue
        cwnd[src][dst] = np.vstack((cwnd[src][dst], (d[0], d[3])))
    return cwnd


#
# t ----------------------------------------->
#    init  |   training   |    test         |
#       init_time      training_time    test_time
#

def get_output(input_file, target_file):
    dt = 0.01
    init_time = 1.0
    training_time = 20.0
    test_time = 40.0

    #(time, src, dst, cwnd)
    data = np.loadtxt(input_file, usecols=(1, 3, 7, 17))

    N = int(np.max(data[:, 1]))+1
    T = int((training_time-init_time)/dt)
    Tall = int(test_time/dt)

    cwnd_timeseries = np.zeros((N*N-N, Tall))

    for d in data:
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

        #print src, dst, idx
        time_idx = int(time/dt)

        if 0 <= time_idx:
            cwnd_timeseries[idx, time_idx:] = cwnd

    #target_data = np.loadtxt(target_file, delimiter=',')
    target_data = np.zeros((1, Tall))
    for i in range(0, int(test_time), 4):
        t0 = int(i/dt)
        t1 = int((i+1)/dt)
        t2 = int((i+2)/dt)
        t3 = int((i+3)/dt)
        t4 = int((i+4)/dt)
        target_data[0, t0:t1] = 0.0
        target_data[0, t1:t2] = 1.0
        target_data[0, t2:t3] = 1.0
        target_data[0, t3:t4] = 0.0

    # train the output
    reg = 1e-8  # regularization coefficient
    X = cwnd_timeseries[:, int(init_time/dt): int(training_time/dt)]
    X_T = X.T
    Yt = target_data[:, int(init_time/dt): int(training_time/dt)]
    Wout = dot(dot(Yt, X_T), linalg.inv(dot(X, X_T) + reg*eye(X.shape[0])))
    #Wout = dot( dot(Yt,X_T), linalg.inv( dot(X,X_T)))

    Y = dot(Wout, cwnd_timeseries)
    R = target_data

    plt.figure(0).clear()
    plt.bar(range(Wout.shape[1]), Wout.T)
    plt.title('Output weights $\mathbf{W}^{out}$')

    plt.figure(1).clear()
    plt.plot(dt*np.arange(Y.shape[1]), Y.T)
    plt.plot(dt*np.arange(R.shape[1]), R.T)
    plt.axvline(x=init_time, color='red')
    plt.axvline(x=training_time, color='red')

    # # check plot
    # plt.figure(10).clear()
    # plt.plot(range(target_data.shape[1]), target_data.T)
    # plt.ylim(0,1.5)
    # plt.plot(frange(init_time, training_time, dt)[:-1],
    #          cwnd_timeseries[89, :])
    # src = 9
    # dst = 8
    # cwnd_raw = convert_cwnd_matrix(data)
    # target = cwnd_raw[src][dst]
    # plt.plot(target[:,0], target[:,1], '.')
    # #plt.plot(target[:,0], target[:,1], drawstyle='steps-post')
    # plt.ylim(1,40)

    plt.show()


if __name__ == '__main__':
    get_output(sys.argv[1], sys.argv[2])
