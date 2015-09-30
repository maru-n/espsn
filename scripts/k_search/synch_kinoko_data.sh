#!/bin/bash
rsync -avz --delete kinoko.c.u-tokyo.ac.jp:~/espsn/scripts/k_search/\*.npy ./
rsync -avz --delete kinoko.c.u-tokyo.ac.jp:~/espsn/scripts/k_search/\*.settings.json ./
#rsync -avz --delete kinoko.c.u-tokyo.ac.jp:~/espsn/scripts/N-T_search/data/\* ./data
