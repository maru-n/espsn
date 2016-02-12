#!/usr/bin/env python

import numpy as np
import random
import os
import util


def generate_settings(input_type, N=10, duration=200,
                      one_signal_duration=4.,
                      k=6.,
                      esn_init_time=4,
                      esn_training_time=100,
                      esn_dt=0.1,
                      continuous_target_delay=0,
                      continuous_time_series_file=None):
    setting_str = ""

    setting_str += ("N:%d\n" % N)
    setting_str += ("duration:%d\n" % duration)
    setting_str += ("link_bps:10Mb\n")
    #setting_str += ("link_delay:10ms\n")
    setting_str += ("link_delay:30ms\n")
    #setting_str += ("link_queue:10\n")
    setting_str += ("link_queue:3\n")
    setting_str += ("k:%f\n" % k)
    setting_str += ("esn_init_time:%d\n" % esn_init_time)
    setting_str += ("esn_training_time:%d\n" % esn_training_time)
    setting_str += ("esn_dt:%f\n" % esn_dt)
    setting_str += "input_num:2\n"  if input_type in ['xor'] else "input_num:1\n"
    setting_str += "continuous:1\n" if input_type in ['continuous', 'continuous-noise'] else "continuous:0\n"
    setting_str += "\n"

    # Topology  [src] [dst] [input_channel] [positive(1)/negative(-1)]
    if input_type in ['xor']:
        setting_str += generate_topology_setting(N, k, 2)
    else:
        setting_str += generate_topology_setting(N, k, 1)

    # Time series  [time] [input0] [input1] ... [target]
    setting_str += "\n"
    if input_type == 'xor':
        setting_str += generate_xor_timeseries(duration, one_signal_duration)
    elif input_type == 'parity':
        setting_str += generate_parity_timeseries(duration, one_signal_duration)
    elif input_type == 'delay':
        setting_str += generate_delay_timeseries(duration, one_signal_duration)
    elif input_type == 'sin':
        setting_str += generate_sin_timeseries(duration, one_signal_duration)
    elif input_type == "continuous":
        setting_str += generate_continuous_timeseries(continuous_time_series_file,
                                                      duration,
                                                      one_signal_duration,
                                                      continuous_target_delay,
                                                      noise=False)
    elif type == "continuous-noise":
        setting_str += generate_continuous_timeseries(continuous_time_series_file,
                                                      duration,
                                                      one_signal_duration,
                                                      continuous_target_delay,
                                                      noise=True)
    return setting_str


def generate_topology_setting(N, k, channel_num):
    result = ""
    p = float(k) / (N - 1.)
    for i in range(N):
        for j in range(N):
            if i != j and random.random() < p:
                result += ("%d %d %d %d\n" % (i, j, random.randint(0, channel_num-1), random.choice([-1,1])))
    return result


def generate_continuous_timeseries(filename, duration, one_signal_duration, target_delay, noise=False):
    noise_standard_deviation = 0.01
    result = ""
    step_num = int(duration/one_signal_duration)
    x = np.loadtxt(filename)
    for i in range(step_num):
        time = float(i * one_signal_duration)
        input_val = x[i]
        target_val = x[i+target_delay]
        if noise:
            input_val += np.random.normal(scale=noise_standard_deviation)
        signal_dt = one_signal_duration * util.continuous_pwm_func(input_val)

        result += ("%f %d %f %f\n" % (time,           1, input_val, target_val))
        result += ("%f %d\n"       % (time+signal_dt, 0))
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

    in1 = [random.randint(0, 1) for i in range(step_num)]
    in2 = [random.randint(0, 1) for i in range(step_num)]

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

    in1 = [random.randint(0, 1) for i in range(step_num)]

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

    in1 = [random.randint(0, 1) for i in range(step_num)]

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
                      default=None,
                      help="write output to FILE",
                      metavar="FILE")
    parser.add_option("-t",
                      "--input-type",
                      dest="input_type",
                      choices=["xor", "parity", "delay", "sin", "continuous", "continuous-noise"],
                      type="choice",
                      default="xor",
                      help="time series type [xor|parity|delay|sin|continuous|continuous-noise]")
    parser.add_option("--time-series-file",
                      dest="time_series_file",
                      type="string",
                      default=None,
                      help="file of continuous time series (ignored when type is not continuous|continuous-noise)")
    parser.add_option("--target-delay",
                      dest="target_delay",
                      type="int",
                      default=1,
                      help="delay of target signal = predictive time step (ignored when type is not continuous|continuous-noise)")
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
                      default=2100,
                      help="experimental duration")
    parser.add_option("--init-time",
                      dest="init_time",
                      type="int",
                      default=100,
                      help="end time of initializaion (< duration)")
    parser.add_option("--training-time",
                      dest="training_time",
                      type="int",
                      default=1100,
                      help="end time of training (< duration)")
    parser.add_option("--esn-dt",
                      dest="esn_dt",
                      type="float",
                      default=4.0,
                      help="duration of a 0/1 signal")
    parser.add_option("--one-signal-duration",
                      dest="one_signal_duration",
                      type="float",
                      default=4.0,
                      help="duration of a 0/1 signal")

    (opts, args) = parser.parse_args()

    random.seed(opts.random_seed)

    settings = generate_settings(opts.input_type,
                                 N=opts.N,
                                 duration=opts.duration,
                                 one_signal_duration=opts.one_signal_duration,
                                 k=opts.k,
                                 esn_init_time=opts.init_time,
                                 esn_training_time=opts.training_time,
                                 esn_dt=opts.esn_dt,
                                 continuous_target_delay=opts.target_delay,
                                 continuous_time_series_file=opts.time_series_file)

    if opts.output_filename is None:
        print(settings)
    else:
        output = open(opts.output_filename, 'w')
        output.write(settings)
