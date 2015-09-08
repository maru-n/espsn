#!/usr/bin/env python

import numpy as np


def generate_settings(type, N=10, duration=200,
                      one_signal_duration=4.,
                      k=6.,
                      esn_init_time=4,
                      esn_training_time=100,
                      esn_dt=0.1):

    setting_str = ""

    setting_str += ("N:%d\n" % N)
    setting_str += ("duration:%d\n" % duration)
    setting_str += ("link_bps:10Mb\n")
    setting_str += ("link_delay:10ms\n")
    setting_str += ("link_queue:10\n")
    #setting_str += ("duty_low:%f\n")
    #setting_str += ("duty_high:%f\n")
    setting_str += ("k:%f\n" % k)
    setting_str += ("esn_init_time:%f\n" % esn_init_time)
    setting_str += ("esn_training_time:%f\n" % esn_training_time)
    setting_str += ("esn_dt:%f\n" % esn_dt)

    if type == 'xor':
        setting_str += ("input:2\n")
        setting_str += ("\n")

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
            setting_str += ("%f %d %d %d\n" % (time, in1[i], in2[i], target))

    elif type == 'parity':
        setting_str += "input:1\n"
        setting_str += "\n"

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
            setting_str += ("%f %d %d\n" % (time, in1[i], target))

    elif type == 'delay':
        setting_str += "input:1\n"
        setting_str += "\n"

        step_num = int(duration/one_signal_duration)

        in1 = [np.random.randint(0, 2) for i in range(step_num)]

        current_parity = True
        for i in range(step_num):
            time = float(i * one_signal_duration)
            target = in1[i-1]
            setting_str += ("%f %d %d\n" % (time, in1[i], target))

    return setting_str


from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-o",
                      dest="output_filename",
                      type="string",
                      default="settings.txt",
                      help="write output to FILE",
                      metavar="FILE")
    parser.add_option("-t",
                      "--type",
                      dest="type",
                      choices=["xor", "parity", "delay"],
                      type="choice",
                      default="xor",
                      help="time series type")
    parser.add_option("-N",
                      dest="N",
                      type="int",
                      default=10,
                      help="node num")
    parser.add_option("-k",
                      dest="k",
                      type="int",
                      default=6,
                      help="k")
    parser.add_option("--random-seed",
                      dest="random_seed",
                      type="int",
                      default=None,
                      help="random seed")
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

    (opts, args) = parser.parse_args()

    np.random.seed(opts.random_seed)

    settings = generate_settings(opts.type,
                                 N=opts.N,
                                 duration=opts.duration,
                                 one_signal_duration=opts.one_signal_duration,
                                 k=opts.k,
                                 esn_init_time=opts.init_time,
                                 esn_training_time=opts.training_time,
                                 esn_dt=0.1)

    if opts.output_filename:
        output = open(opts.output_filename, 'w')
        output.write(settings)
    else:
        print(settings)
