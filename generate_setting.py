#!/usr/bin/env python

import numpy as np
from numpy.random import random, randint

def generate_settings(type, N=10, duration=200,
                      one_signal_duration=4.,
                      k=6.,
                      esn_init_time=4,
                      esn_training_time=100,
                      esn_dt=0.1,
                      data_delay=0):
    setting_str = ""

    setting_str += ("N:%d\n" % N)
    setting_str += ("duration:%d\n" % duration)
    setting_str += ("link_bps:10Mb\n")
    #setting_str += ("link_delay:10ms\n")
    setting_str += ("link_delay:30ms\n")
    #setting_str += ("link_queue:10\n")
    setting_str += ("link_queue:3\n")
    setting_str += ("k:%f\n" % k)
    setting_str += ("esn_init_time:%f\n" % esn_init_time)
    setting_str += ("esn_training_time:%f\n" % esn_training_time)
    setting_str += ("esn_dt:%f\n" % esn_dt)
    if type in ['xor']:
        channel_num = 2
    else:
        channel_num = 1
    setting_str += "input:%d\n" % channel_num

    # Topology  [src] [dst] [input_channel] [positive/negative]
    setting_str += "\n"
    setting_str += generate_topology_setting(N, k, channel_num)

    # Time series  [time] [input0] [input1] ... [target]
    setting_str += "\n"
    if type == 'xor':
        setting_str += generate_xor_timeseries(duration, one_signal_duration)
    elif type == 'parity':
        setting_str += generate_parity_timeseries(duration, one_signal_duration)
    elif type == 'delay':
        setting_str += generate_delay_timeseries(duration, one_signal_duration)
    elif type == 'sin':
        setting_str += generate_sin_timeseries(duration, one_signal_duration)
    elif type == "mg":
        setting_str += generate_mackey_glass_timeseries(duration, one_signal_duration, dt=data_delay)

    return setting_str


def generate_topology_setting(N, k, channel_num):
    result = ""
    p = float(k) / (N - 1.)
    for i in range(N):
        for j in range(N):
            if i != j and random() < p:
                result += ("%d %d %d %d\n" % (i, j, randint(0, channel_num), randint(0,2)))
    return result

#from scipy.integrate import ode

def generate_mackey_glass_timeseries(duration, one_signal_duration, dt=0):
    result = ""
    step_num = int(duration/one_signal_duration)
    x = np.loadtxt("MackeyGlass_t17.txt")
    for i in range(step_num):
        time = float(i * one_signal_duration)
        input_val = x[i] + 0.6
        target_val = x[i+dt] + 0.6
        signal_dt = one_signal_duration * input_val
        result += ("%f 1 %f %f\n" % (time, input_val, target_val))
        result += ("%f 0 %f %f\n" % (time+signal_dt, input_val, target_val))
    return result


def generate_sin_timeseries(duration, one_signal_duration):
    result = ""
    step_num = int(duration/one_signal_duration)

    for i in range(step_num):
        time = float(i * one_signal_duration)
        th = (time/30) % (2.0*np.pi)
        target = np.sin(th)*0.5 + 0.5
        dt = one_signal_duration * target
        #dt = one_signal_duration * th / (2.0*np.pi)

        result += ("%f 1 %f\n" % (time, target))
        result += ("%f 0 %f\n" % (time+dt, target))
    return result


def generate_xor_timeseries(duration, one_signal_duration):
    result = ""
    step_num = int(duration/one_signal_duration)

    in1 = [np.random.randint(0, 2) for i in range(step_num)]
    in2 = [np.random.randint(0, 2) for i in range(step_num)]

    for i in range(step_num):
        time = float(i * one_signal_duration)

        # network condition is not changed
        if i != 0 and in1[i] == in1[i-1] and in2[i] == in2[i-1]:
            continue

        if (in1[i] == 1 and in2[i] == 1) or (in1[i] == 0 and in2[i] == 0):
            target = 0
        else:
            target = 1
        result += ("%f %d %d %d\n" % (time, in1[i], in2[i], target))
    return result


def generate_parity_timeseries(duration, one_signal_duration):
    result = ""
    step_num = int(duration/one_signal_duration)

    in1 = [np.random.randint(0, 2) for i in range(step_num)]

    current_parity = True
    for i in range(step_num):
        time = float(i * one_signal_duration)

        if in1[i] == 1:
            current_parity = not current_parity

        # network condition is not changed
        if i != 0 and in1[i] == in1[i-1] == 0:
            continue

        target = 1 if current_parity else 0
        result += ("%f %d %d\n" % (time, in1[i], target))
    return result


def generate_delay_timeseries(duration, one_signal_duration):
    result = ""
    step_num = int(duration/one_signal_duration)

    in1 = [np.random.randint(0, 2) for i in range(step_num)]

    current_parity = True
    for i in range(step_num):
        time = float(i * one_signal_duration)
        target = in1[i-1]
        result += ("%f %d %d\n" % (time, in1[i], target))
    return result


from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-o",
                      dest="output_filename",
                      type="string",
                      default="setting.txt",
                      help="write output to FILE",
                      metavar="FILE")
    parser.add_option("-t",
                      "--type",
                      dest="type",
                      choices=["xor", "parity", "delay", "sin", "mg"],
                      type="choice",
                      default="xor",
                      help="time series type [xor|parity|delay|sin|mg]")
    parser.add_option("-N",
                      dest="N",
                      type="int",
                      default=16,
                      help="node num")
    parser.add_option("-k",
                      dest="k",
                      type="float",
                      default=4.0,
                      help="k")
    parser.add_option("--random-seed",
                      dest="random_seed",
                      type="int",
                      default=None,
                      help="random seed for generate settings")
    parser.add_option("--duration",
                      dest="duration",
                      type="int",
                      default=500,
                      help="experimental duration")
    parser.add_option("--init-time",
                      dest="init_time",
                      type="int",
                      default=100,
                      help="end time of initializaion (< duration)")
    parser.add_option("--training-time",
                      dest="training_time",
                      type="int",
                      default=300,
                      help="end time of training (< duration)")
    parser.add_option("--one-signal-duration",
                      dest="one_signal_duration",
                      type="float",
                      default=4.0,
                      help="duration of a 0/1 signal")
    parser.add_option("--data-delay",
                      dest="data_delay",
                      type="int",
                      default=0,
                      help="data delay (continuous value only)")

    (opts, args) = parser.parse_args()

    np.random.seed(opts.random_seed)

    settings = generate_settings(opts.type,
                                 N=opts.N,
                                 duration=opts.duration,
                                 one_signal_duration=opts.one_signal_duration,
                                 k=opts.k,
                                 esn_init_time=opts.init_time,
                                 esn_training_time=opts.training_time,
                                 esn_dt=0.1,
                                 data_delay=opts.data_delay)

    if opts.output_filename:
        output = open(opts.output_filename, 'w')
        output.write(settings)
    else:
        print(settings)
