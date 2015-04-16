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
    N = int(np.max(raw_data[:, 1])) + 1
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
    training_time = 50.0
    test_time = 80.0
    #training_time = 50.0
    #test_time = 120.0

    #(time, src, dst, cwnd)
    data = np.loadtxt(input_file, usecols=(1, 3, 7, 17))

    N = int(np.max(data[:, 1])) + 1
    T = int((training_time - init_time) / dt)
    Tall = int(test_time / dt)

    cwnd_timeseries = np.zeros((N * N - N, Tall))

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

        # print src, dst, idx
        time_idx = int(time / dt)

        if 0 <= time_idx:
            cwnd_timeseries[idx, time_idx:] = cwnd

    target_data_raw = np.loadtxt(target_file)
    target_data = np.zeros((1, Tall))
    input_data1 = np.zeros((1, Tall))
    input_data2 = np.zeros((1, Tall))

    for i in range(len(target_data_raw)):
        target_data[0, i] = target_data_raw[i, 0]
        input_data1[0, i] = target_data_raw[i, 1] / 4. - 0.5
        input_data2[0, i] = target_data_raw[i, 2] / 4. - 0.9

    # train the output
    ############
    # reg = 1e-8  # regularization coefficient
    ############
    reg = 1e-6  # regularization coefficient
    X = cwnd_timeseries[:, int(init_time / dt): int(training_time / dt)]
    X_T = X.T
    Yt = target_data[:, int(init_time / dt): int(training_time / dt)]
    Wout = dot(dot(Yt, X_T), linalg.inv(dot(X, X_T) + reg * eye(X.shape[0])))
    #Wout = dot( dot(Yt,X_T), linalg.inv( dot(X,X_T)))

    # compute MSE for the first errorLen time steps
    #mse = sum(square(data[trainLen+1:trainLen+errorLen+1] - Y[0,0:errorLen])) / errorLen
    # print 'MSE = ' + str( mse )

    Y = dot(Wout, cwnd_timeseries)
    R = target_data

    plt.figure(0).clear()
    plt.bar(range(Wout.shape[1]), Wout.T)
    plt.title('Output weights $\mathbf{W}^{out}$')

    plt.figure(1).clear()
    plt.plot(dt * np.arange(R.shape[1]), R.T, 'r', linewidth=2)
    plt.plot(dt * np.arange(input_data1.shape[1]),
             input_data1.T, 'g', linewidth=2)
    plt.plot(dt * np.arange(input_data2.shape[1]),
             input_data2.T, 'g', linewidth=2)
    plt.axvline(x=init_time, color='red')
    plt.axvline(x=training_time, color='red')
    plt.plot(dt * np.arange(Y.shape[1]), Y.T, 'b')

    # check plot
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
    # plt.plot(target[:,0], target[:,1], drawstyle='steps-post')
    # plt.ylim(1,40)

    plt.show()


if __name__ == '__main__':
    get_output(sys.argv[1], sys.argv[2])
