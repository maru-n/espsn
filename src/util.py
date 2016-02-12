#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def sigmoid(x, a=1):
    return 1/(1+np.exp(-a*x))


def continuous_pwm_func(x):
    return max(0., x*0.5 + 0.5)
    #return sigmoid(x)


def print_status(msg, end="\n", header="[ESN]"):
    print("\033[34m" + header + "\033[39m " + msg, end=end)
