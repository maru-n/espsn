#!/usr/bin/env python

import numpy as np

RONDOM_SEED = None


def generate_settings(type, N=10, duration=200,
                      one_signal_duration=4,
                      esn_init_time=4,
                      esn_training_time=100,
                      esn_dt=0.1):

    setting_str = ""

    setting_str += ("N:%d\n" % N)
    setting_str += ("duration:%d\n" % duration)
    setting_str += ("link_bps:10Mb\n")
    setting_str += ("link_delay:10ms\n")
    setting_str += ("link_queue:10\n")
    setting_str += ("esn_init_time:%f\n" % esn_init_time)
    setting_str += ("esn_training_time:%f\n" % esn_training_time)
    setting_str += ("esn_dt:%f\n" % esn_dt)

    if type == 'xor':
        setting_str += ("input:2\n")
        setting_str += ("\n")

        step_num = duration/one_signal_duration

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

        step_num = duration/one_signal_duration

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
    parser.add_option("-r",
                      dest="random_seed",
                      type='int',
                      default=None,
                      help="random seed value", metavar="SEED")
    parser.add_option("-t",
                      "--type",
                      dest="type",
                      choices=["xor", "parity"],
                      type="choice",
                      default="xor",
                      help="time series type")
    parser.add_option("-N",
                      dest="N",
                      type="int",
                      default=10,
                      help="node num")

    (options, args) = parser.parse_args()

    np.random.seed(options.random_seed)

    settings = generate_settings(options.type,
                                 N=options.N,
                                 duration=400,
                                 one_signal_duration=4,
                                 esn_init_time=4,
                                 esn_training_time=200,
                                 esn_dt=0.1)

    if options.output_filename:
        output = open(options.output_filename, 'w')
        output.write(settings)
    else:
        print settings
