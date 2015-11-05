#!/usr/bin/env python

import random
import numpy as np
import sys

esn_dt = 0.1

output_time = 0.0
time = 0.0

while True:
    line = sys.stdin.readline()
    if(line == "get_activity\n"):
        #print(random.random())
        print(time)
        sys.stdout.flush()
    else:
        vals = line.split()
        time = float(vals[0])
        src = int(vals[1])
        dst = int(vals[3])
        cwnd = float(vals[6])
